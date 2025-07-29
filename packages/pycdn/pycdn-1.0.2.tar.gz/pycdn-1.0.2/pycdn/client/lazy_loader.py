"""
Lazy loading mechanism for CDN packages.
"""

import sys
import inspect
from types import ModuleType
from typing import Any, Dict, Optional, Callable, Union
import httpx

from ..utils.common import serialize_args, deserialize_result, log_debug


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
            # The instance will be created on the server side when methods are called
            log_debug(f"Lazy instance of {self._class_name} created with args: {len(self._init_args)} args, {len(self._init_kwargs)} kwargs")
            
        except Exception as e:
            log_debug(f"Failed to initialize remote instance: {e}")
            raise e
    
    def __getattr__(self, name: str) -> Any:
        """
        Lazy loading of instance attributes and methods.
        
        Args:
            name: Attribute name
            
        Returns:
            Lazy attribute wrapper
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self._class_name}' object has no attribute '{name}'")
        
        # Return lazy method wrapper
        method_name = f"{self._class_name}.{name}"
        return LazyMethod(
            self._cdn_client,
            self._package_name,
            method_name,
            self
        )
    
    def __repr__(self) -> str:
        return f"<LazyInstance of '{self._class_name}' from '{self._cdn_client.url}'>"


class LazyMethod:
    """
    Lazy wrapper for remote instance methods.
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
            method_name: Name of the method
            instance: Parent lazy instance
        """
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._method_name = method_name
        self._instance = instance
    
    def __call__(self, *args, **kwargs) -> Any:
        """
        Execute the remote method.
        
        Args:
            *args: Method arguments
            **kwargs: Method keyword arguments
            
        Returns:
            Method execution result
        """
        log_debug(f"Executing lazy method {self._method_name}")
        
        try:
            # Create a special request for instance methods that includes instance creation
            request_data = {
                "instance_info": {
                    "class_name": self._instance._class_name,
                    "init_args": self._instance._init_args,
                    "init_kwargs": self._instance._init_kwargs
                },
                "method_args": args,
                "method_kwargs": kwargs
            }
            
            # Serialize the request data
            serialized_args = serialize_args(request_data)
            
            # Execute remote method
            response = self._cdn_client._execute_request(
                self._package_name,
                self._method_name,
                serialized_args
            )
            
            return deserialize_result(response)
            
        except Exception as e:
            log_debug(f"Lazy method execution failed: {e}")
            raise e


class LazyModule(ModuleType):
    """
    Lazy module wrapper for CDN packages.
    """
    
    def __init__(self, cdn_client: "CDNClient", package_name: str):
        """
        Initialize lazy module.
        
        Args:
            cdn_client: CDN client instance
            package_name: Name of the package
        """
        super().__init__(package_name)
        
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._loaded_attributes = {}
        self._package_info = None
        
        # Set module metadata
        self.__name__ = package_name
        self.__package__ = package_name
        self.__spec__ = None
        self.__file__ = f"<CDN:{cdn_client.url}/{package_name}>"
        self.__loader__ = None
        
        # Load package information
        self._load_package_info()
    
    def _load_package_info(self) -> None:
        """Load package information from CDN server."""
        try:
            self._package_info = self._cdn_client.get_package_info(self._package_name)
            log_debug(f"Loaded package info for {self._package_name}")
        except Exception as e:
            log_debug(f"Failed to load package info: {e}")
            self._package_info = {"attributes": []}
    
    def __getattr__(self, name: str) -> Any:
        """
        Lazy loading of module attributes.
        
        Args:
            name: Attribute name
            
        Returns:
            Lazy attribute wrapper
        """
        if name.startswith('_'):
            raise AttributeError(f"module '{self._package_name}' has no attribute '{name}'")
        
        # Check if already loaded
        if name in self._loaded_attributes:
            return self._loaded_attributes[name]
        
        # Check if attribute exists in package info
        if self._package_info:
            for attr in self._package_info.get("attributes", []):
                if attr["name"] == name:
                    # Create appropriate lazy wrapper
                    if attr.get("callable", False):
                        if attr.get("type") == "type":  # Class
                            wrapper = LazyClass(
                                self._cdn_client,
                                self._package_name,
                                name,
                                f"{self._package_name}.{name}"
                            )
                        else:  # Function
                            wrapper = LazyFunction(
                                self._cdn_client,
                                self._package_name,
                                name,
                                f"{self._package_name}.{name}"
                            )
                    else:
                        # For non-callable attributes, we need to fetch the value
                        wrapper = self._get_remote_attribute(name)
                    
                    self._loaded_attributes[name] = wrapper
                    return wrapper
        
        # If not found in package info, try to create a lazy function anyway
        wrapper = LazyFunction(
            self._cdn_client,
            self._package_name,
            name,
            f"{self._package_name}.{name}"
        )
        self._loaded_attributes[name] = wrapper
        return wrapper
    
    def _get_remote_attribute(self, name: str) -> Any:
        """
        Get a remote attribute value.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute value
        """
        try:
            # Use a special function to get attribute values
            serialized_args = serialize_args()
            response = self._cdn_client._execute_request(
                self._package_name,
                f"__getattr__.{name}",
                serialized_args
            )
            return deserialize_result(response)
        except Exception as e:
            log_debug(f"Failed to get remote attribute {name}: {e}")
            return None
    
    def __repr__(self) -> str:
        return f"<LazyModule '{self._package_name}' from '{self._cdn_client.url}'>"
    
    def __dir__(self) -> list:
        """Return list of available attributes."""
        attrs = list(self._loaded_attributes.keys())
        if self._package_info:
            attrs.extend([attr["name"] for attr in self._package_info.get("attributes", [])])
        return sorted(set(attrs))


class LazyPackage:
    """
    Lazy package namespace for CDN packages.
    """
    
    def __init__(self, cdn_client: "CDNClient"):
        """
        Initialize lazy package.
        
        Args:
            cdn_client: CDN client instance
        """
        self._cdn_client = cdn_client
        self._loaded_modules = {}
    
    def __getattr__(self, name: str) -> LazyModule:
        """
        Lazy loading of package modules.
        
        Args:
            name: Module name
            
        Returns:
            LazyModule instance
        """
        if name.startswith('_'):
            raise AttributeError(f"No attribute '{name}'")
        
        # Check if already loaded
        if name in self._loaded_modules:
            return self._loaded_modules[name]
        
        # Create lazy module
        module = LazyModule(self._cdn_client, name)
        self._loaded_modules[name] = module
        
        return module
    
    def __repr__(self) -> str:
        return f"<LazyPackage from '{self._cdn_client.url}'>"
    
    def __dir__(self) -> list:
        """Return list of available modules."""
        return sorted(self._loaded_modules.keys()) 