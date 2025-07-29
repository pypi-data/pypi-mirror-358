"""
Lazy loading mechanism for CDN packages - Updated for Hybrid System.
"""

import sys
import inspect
from types import ModuleType
from typing import Any, Dict, Optional, List, Callable, Union
import httpx

from ..utils.common import serialize_args, deserialize_result, log_debug
from ..utils.encryption import get_global_encryption
from .import_hook import register_hybrid_cdn, HybridCDNProxy


class LazyFunction:
    """
    Lazy wrapper for remote functions.
    """
    
    def __init__(
        self,
        cdn_client: "CDNClient",
        package_name: str,
        function_name: str,
        full_name: str
    ):
        """
        Initialize lazy function.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
            function_name: Name of the function
            full_name: Full qualified name (package.function)
        """
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._function_name = function_name
        self._full_name = full_name
        self._cached_metadata = None
        
        # Set function metadata
        self.__name__ = function_name
        self.__qualname__ = full_name
        self.__module__ = package_name
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the remote function.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function execution result
        """
        log_debug(f"Executing lazy function {self._full_name}")
        
        try:
            # Serialize arguments
            serialized_args = serialize_args(*args, **kwargs)
            
            # Make request to CDN server
            response = self._cdn_client._execute_request(
                self._package_name,
                self._function_name,
                serialized_args
            )
            
            # Deserialize and return result
            return deserialize_result(response)
            
        except Exception as e:
            log_debug(f"Lazy function execution failed: {e}")
            raise e
    
    def __repr__(self) -> str:
        return f"<LazyFunction '{self._full_name}' from '{self._cdn_client.url}'>"
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def __getattr__(self, name: str) -> "LazyAttribute":
        """
        Support chained attribute access for function results.
        
        Args:
            name: Attribute name
            
        Returns:
            LazyAttribute for chained access
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self._full_name}' object has no attribute '{name}'")
        
        # Create a lazy attribute for chained access
        attribute_path = f"{self._function_name}.{name}"
        return LazyAttribute(
            self._cdn_client,
            self._package_name,
            attribute_path,
            None  # No instance for module-level functions
        )


class LazyClass:
    """
    Lazy wrapper for remote classes.
    """
    
    def __init__(
        self,
        cdn_client: "CDNClient",
        package_name: str,
        class_name: str,
        full_name: str
    ):
        """
        Initialize lazy class.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
            class_name: Name of the class
            full_name: Full qualified name
        """
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._class_name = class_name
        self._full_name = full_name
        
        # Set class metadata
        self.__name__ = class_name
        self.__qualname__ = full_name
        self.__module__ = package_name
    
    def __call__(self, *args, **kwargs) -> "LazyInstance":
        """
        Create a lazy instance of the class.
        
        Args:
            *args: Constructor arguments
            **kwargs: Constructor keyword arguments
            
        Returns:
            LazyInstance object
        """
        log_debug(f"Creating lazy instance of {self._full_name}")
        
        # Create lazy instance
        return LazyInstance(
            self._cdn_client,
            self._package_name,
            self._class_name,
            args,
            kwargs
        )
    
    def __repr__(self) -> str:
        return f"<LazyClass '{self._full_name}' from '{self._cdn_client.url}'>"


class LazyInstance:
    """
    Lazy wrapper for remote class instances.
    """
    
    def __init__(
        self,
        cdn_client: "CDNClient",
        package_name: str,
        class_name: str,
        init_args: tuple,
        init_kwargs: dict
    ):
        """
        Initialize lazy instance.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
            class_name: Name of the class
            init_args: Constructor arguments
            init_kwargs: Constructor keyword arguments
        """
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._class_name = class_name
        self._init_args = init_args
        self._init_kwargs = init_kwargs
        self._instance_id = None  # Would be used for stateful instances
        
        # Initialize the remote instance
        self._initialize_remote_instance()
    
    def _initialize_remote_instance(self) -> None:
        """Initialize the remote instance."""
        try:
            # For MVP, we skip actual remote instance creation and delegate to method calls
            log_debug(f"Initialized lazy instance of {self._class_name}")
        except Exception as e:
            log_debug(f"Failed to initialize remote instance: {e}")
            raise e
    
    def __getattr__(self, name: str) -> Any:
        """
        Lazy attribute access for instance members.
        
        Args:
            name: Attribute name
            
        Returns:
            LazyMethod for methods or LazyAttribute for other attributes
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self._class_name}' instance has no attribute '{name}'")
        
        # Try to determine if this is a method or attribute
        # For MVP, we assume everything is a method
        return LazyMethod(
            self._cdn_client,
            self._package_name,
            f"{self._class_name}.{name}",
            self
        )
    
    def __repr__(self) -> str:
        return f"<LazyInstance of '{self._package_name}.{self._class_name}' from '{self._cdn_client.url}'>"


class LazyAttribute:
    """
    Lazy wrapper for remote attributes (including nested attributes).
    """
    
    def __init__(
        self,
        cdn_client: "CDNClient",
        package_name: str,
        attribute_path: str,
        instance: LazyInstance = None
    ):
        """
        Initialize lazy attribute.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
            attribute_path: Full path to the attribute (e.g., "module.Class.attribute")
            instance: Parent instance if this is an instance attribute
        """
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._attribute_path = attribute_path
        self._instance = instance
        
        # Set metadata
        parts = attribute_path.split('.')
        self.__name__ = parts[-1]
        self.__qualname__ = attribute_path
        self.__module__ = package_name
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the attribute as a callable.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Execution result
        """
        log_debug(f"Executing lazy attribute {self._attribute_path}")
        
        try:
            # Serialize arguments
            serialized_args = serialize_args(*args, **kwargs)
            
            # Prepare request data
            request_data = {
                'package_name': self._package_name,
                'function_name': self._attribute_path,
                'serialized_args': serialized_args
            }
            
            # Add instance context if this is an instance method
            if self._instance and hasattr(self._instance, '_init_args'):
                request_data['instance_args'] = self._instance._init_args
                request_data['instance_kwargs'] = self._instance._init_kwargs
            
            # Make request to CDN server
            response = self._cdn_client._execute_request(
                self._package_name,
                self._attribute_path,
                serialized_args
            )
            
            # Deserialize and return result
            return deserialize_result(response)
            
        except Exception as e:
            log_debug(f"Lazy attribute execution failed: {e}")
            raise e
    
    def __getattr__(self, name: str) -> "LazyAttribute":
        """
        Support chained attribute access.
        
        Args:
            name: Attribute name
            
        Returns:
            LazyAttribute for chained access
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self._attribute_path}' object has no attribute '{name}'")
        
        # Create nested attribute path
        nested_path = f"{self._attribute_path}.{name}"
        return LazyAttribute(
            self._cdn_client,
            self._package_name,
            nested_path,
            self._instance
        )
    
    def __repr__(self) -> str:
        instance_info = f" (instance)" if self._instance else ""
        return f"<LazyAttribute '{self._attribute_path}'{instance_info} from '{self._cdn_client.url}'>"


class LazyMethod(LazyAttribute):
    """
    Specialized lazy wrapper for remote methods.
    """
    
    def __init__(
        self,
        cdn_client: "CDNClient",
        package_name: str,
        method_name: str,
        instance: LazyInstance
    ):
        """
        Initialize lazy method.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
            method_name: Name of the method (e.g., "Class.method")
            instance: Parent instance
        """
        super().__init__(cdn_client, package_name, method_name, instance)
        self._method_name = method_name


class LazyModule(ModuleType):
    """
    Lazy module that loads package information on-demand.
    """
    
    def __init__(self, cdn_client: "CDNClient", package_name: str):
        """
        Initialize lazy module.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
        """
        super().__init__(package_name)
        
        # Store CDN client reference
        object.__setattr__(self, '_cdn_client', cdn_client)
        object.__setattr__(self, '_package_name', package_name)
        object.__setattr__(self, '_loaded_attributes', set())
        object.__setattr__(self, '_package_info', None)
        
        # Set module metadata
        self.__name__ = package_name
        self.__package__ = package_name
        self.__path__ = [f"cdn://{cdn_client.url}/{package_name}"]
        
        log_debug(f"Created lazy module for {package_name}")
        
        # Load basic package information
        self._load_package_info()
    
    def _load_package_info(self) -> None:
        """Load basic package information from the CDN server."""
        try:
            # This could fetch package metadata like available classes/functions
            pass
        except Exception as e:
            log_debug(f"Failed to load package info for {self._package_name}: {e}")
    
    def __getattr__(self, name: str) -> Any:
        """
        Lazy attribute resolution for the module.
        
        Args:
            name: Attribute name
            
        Returns:
            Resolved attribute (LazyClass, LazyFunction, or LazyAttribute)
        """
        if name.startswith('_'):
            raise AttributeError(f"module '{self._package_name}' has no attribute '{name}'")
        
        # Check if we've already loaded this attribute
        if name in self._loaded_attributes:
            return object.__getattribute__(self, name)
        
        log_debug(f"Lazy loading attribute '{name}' from package '{self._package_name}'")
        
        try:
            # Get remote attribute
            result = self._get_remote_attribute(name)
            
            # Cache the attribute
            object.__setattr__(self, name, result)
            self._loaded_attributes.add(name)
            
            return result
            
        except Exception as e:
            log_debug(f"Failed to load attribute '{name}': {e}")
            raise AttributeError(f"module '{self._package_name}' has no attribute '{name}'")
    
    def _get_remote_attribute(self, name: str) -> Any:
        """
        Get an attribute from the remote CDN server.
        
        Args:
            name: Attribute name
            
        Returns:
            Appropriate lazy wrapper for the attribute
        """
        try:
            # For MVP, we make a simple assumption about attribute types
            # In production, this would query the server for metadata
            
            full_name = f"{self._package_name}.{name}"
            
            # Common class patterns (heuristic-based for MVP)
            if name[0].isupper():  # Likely a class
                return LazyClass(self._cdn_client, self._package_name, name, full_name)
            else:  # Likely a function
                return LazyFunction(self._cdn_client, self._package_name, name, full_name)
                
        except Exception as e:
            log_debug(f"Failed to resolve remote attribute {name}: {e}")
            # Fallback to generic attribute
            return LazyAttribute(self._cdn_client, self._package_name, name)
    
    def __repr__(self) -> str:
        return f"<LazyModule '{self._package_name}' from '{self._cdn_client.url}'>"
    
    def __dir__(self) -> list:
        """Return list of available attributes."""
        # In production, this would query the server for available attributes
        return list(self._loaded_attributes)


class LazyPackage:
    """
    Main entry point for lazy CDN packages with hybrid import support.
    """
    
    def __init__(self, cdn_client: "CDNClient", prefix: str = "cdn"):
        """
        Initialize lazy package with hybrid import support.
        
        Args:
            cdn_client: CDN client instance
            prefix: Import prefix (default: "cdn")
        """
        self._cdn_client = cdn_client
        self._prefix = prefix
        self._loaded_modules = {}
        self._hybrid_root = None
        
        # Automatically enable hybrid imports
        self._enable_hybrid_imports()
        
        log_debug(f"Created lazy package with prefix '{prefix}'")
    
    def _enable_hybrid_imports(self) -> None:
        """Enable hybrid import system for this package."""
        try:
            # Register with the hybrid import system
            self._hybrid_root = register_hybrid_cdn(self._cdn_client, self._prefix)
            log_debug(f"Enabled hybrid imports for prefix '{self._prefix}'")
        except Exception as e:
            log_debug(f"Failed to enable hybrid imports: {e}")
    
    def __getattr__(self, name: str) -> Any:
        """
        Get a lazy module for the given package name.
        
        Args:
            name: Package name
            
        Returns:
            Module proxy (HybridCDNProxy if available, LazyModule as fallback)
        """
        if name.startswith('_'):
            raise AttributeError(f"LazyPackage has no attribute '{name}'")
        
        # If we have hybrid root, delegate to it for consistency
        if self._hybrid_root:
            try:
                return getattr(self._hybrid_root, name)
            except AttributeError:
                pass
        
        # Fallback to legacy LazyModule system
        # Check cache first
        if name in self._loaded_modules:
            return self._loaded_modules[name]
        
        log_debug(f"Creating lazy module for package '{name}'")
        
        # Create lazy module
        lazy_module = LazyModule(self._cdn_client, name)
        
        # Cache it
        self._loaded_modules[name] = lazy_module
        
        return lazy_module
    
    def set_prefix(self, prefix: str) -> None:
        """
        Set a custom import prefix for this CDN connection.
        
        Args:
            prefix: New prefix name (e.g., "mycdn", "internal")
        """
        old_prefix = self._prefix
        self._prefix = prefix
        
        # Re-register with new prefix
        try:
            if self._hybrid_root:
                # Unregister old prefix
                from .import_hook import unregister_hybrid_cdn
                unregister_hybrid_cdn(old_prefix)
                
                # Register with new prefix
                self._hybrid_root = register_hybrid_cdn(self._cdn_client, prefix)
                
            log_debug(f"Changed import prefix from '{old_prefix}' to '{prefix}'")
        except Exception as e:
            log_debug(f"Failed to change prefix: {e}")
            # Revert on failure
            self._prefix = old_prefix
            raise
    
    def reload(self, package_name: str = None) -> str:
        """
        Reload packages (delegated to hybrid system).
        
        Args:
            package_name: Specific package to reload, or None for all
            
        Returns:
            Status message
        """
        if self._hybrid_root:
            return self._hybrid_root.reload(package_name)
        else:
            # Fallback for non-hybrid mode
            if package_name:
                if package_name in self._loaded_modules:
                    del self._loaded_modules[package_name]
                return f"✅ Reloaded {package_name}"
            else:
                self._loaded_modules.clear()
                return "✅ Reloaded all packages"
    
    def profile(self, package_name: str = None) -> Dict[str, Any]:
        """Get profiling data (delegated to hybrid system)."""
        if self._hybrid_root:
            return self._hybrid_root.profile(package_name)
        return {}
    
    def alias(self, original_name: str, alias_name: str) -> str:
        """Create package alias (delegated to hybrid system)."""
        if self._hybrid_root:
            return self._hybrid_root.alias(original_name, alias_name)
        return f"✅ Created alias: {alias_name} -> {original_name}"
    
    def dev_mode(self, enabled: bool = True, local_packages: Dict[str, Any] = None) -> str:
        """Enable dev mode (delegated to hybrid system)."""
        if self._hybrid_root:
            return self._hybrid_root.dev_mode(enabled, local_packages)
        return f"✅ Dev mode {'enabled' if enabled else 'disabled'}"
    
    def list_packages(self) -> List[str]:
        """List available packages (delegated to hybrid system)."""
        if self._hybrid_root:
            return self._hybrid_root.list_packages()
        return list(self._loaded_modules.keys())
    
    def describe(self, symbol_path: str) -> Dict[str, Any]:
        """Describe a symbol (delegated to hybrid system)."""
        if self._hybrid_root:
            return self._hybrid_root.describe(symbol_path)
        return {"error": "Description not available"}
    
    def __repr__(self) -> str:
        return f"<LazyPackage prefix='{self._prefix}' from '{self._cdn_client.url}'>"
    
    def __dir__(self) -> list:
        """Return list of loaded modules."""
        base_attrs = ["reload", "profile", "alias", "dev_mode", "list_packages", "describe", "set_prefix"]
        return base_attrs + list(self._loaded_modules.keys()) 