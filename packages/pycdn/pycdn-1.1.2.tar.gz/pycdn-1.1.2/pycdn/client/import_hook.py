"""
Hybrid PyCDN Import System - Unified Natural & Classic Syntax

This revolutionary implementation provides a single import system supporting:
- Classic access: cdn.openai.OpenAI()
- Natural imports: from cdn.openai import OpenAI
- Smart enhancements: profiling, aliasing, introspection, dev mode

All through the same backend with lazy loading, caching, and proxy system.
"""

import sys
import importlib.machinery
import importlib.util
import importlib.abc
import types
import threading
import time
import traceback
from typing import Any, Dict, Optional, List, Set, Callable, Union
from ..utils.common import log_debug


class PyCDNRemoteError(Exception):
    """Exception raised when remote CDN execution fails."""
    
    def __init__(self, message: str, remote_traceback: str = None, package_name: str = None):
        self.message = message
        self.remote_traceback = remote_traceback
        self.package_name = package_name
        super().__init__(message)
    
    def __str__(self):
        result = f"PyCDN Remote Error: {self.message}"
        if self.package_name:
            result += f" (package: {self.package_name})"
        if self.remote_traceback:
            result += f"\n\nRemote Traceback:\n{self.remote_traceback}"
        return result


class HybridCDNProxy:
    """
    Unified proxy that supports both classic access and import resolution.
    
    This is the core of the hybrid system - it acts as both:
    1. A classic object you can access with cdn.package.Class()
    2. A module that can be imported with 'from cdn.package import Class'
    """
    
    def __init__(self, cdn_client, module_path: str = "", parent=None):
        object.__setattr__(self, '_cdn_client', cdn_client)
        object.__setattr__(self, '_module_path', module_path)
        object.__setattr__(self, '_parent', parent)
        object.__setattr__(self, '_cached_attrs', {})
        object.__setattr__(self, '_access_log', [])
        object.__setattr__(self, '_profile_data', {})
        object.__setattr__(self, '_aliases', {})
        object.__setattr__(self, '_dev_mode', False)
        object.__setattr__(self, '_local_fallbacks', {})
        object.__setattr__(self, '_prefix', module_path or "cdn")  # Set default prefix
        
        # Set required package attributes for Python import system
        object.__setattr__(self, '__path__', [])  # Empty list marks as package
        object.__setattr__(self, '__package__', module_path or "cdn")
        object.__setattr__(self, '__name__', module_path or "cdn")
        object.__setattr__(self, '__spec__', None)
        
        # If this is a module path, register it in sys.modules for imports
        if module_path:
            full_module_name = f"cdn.{module_path}" if module_path != "cdn" else "cdn"
            sys.modules[full_module_name] = self
            log_debug(f"Registered hybrid proxy for {full_module_name}")
        else:
            # This is the root 'cdn' module
            sys.modules["cdn"] = self
            log_debug(f"Registered root hybrid proxy for 'cdn'")
    
    def __getattr__(self, name: str) -> Any:
        """
        Unified attribute resolution for both classic and import access.
        """
        if name.startswith('_'):
            raise AttributeError(f"'{self._module_path}' has no attribute '{name}'")
        
        # Check aliases first
        if name in self._aliases:
            name = self._aliases[name]
        
        # Check cache
        cache_key = name
        if cache_key in self._cached_attrs:
            self._log_access(name, "cache_hit")
            return self._cached_attrs[cache_key]
        
        # Check dev mode fallbacks
        if self._dev_mode and name in self._local_fallbacks:
            return self._local_fallbacks[name]
        
        # Build full path
        if self._module_path and self._module_path != "cdn":
            full_path = f"{self._module_path}.{name}"
            package_name = self._module_path
        else:
            full_path = name
            package_name = name
        
        start_time = time.time()
        
        try:
            # Resolve from CDN server
            result = self._resolve_symbol(package_name, name, full_path)
            
            # Cache the result
            self._cached_attrs[cache_key] = result
            
            # Log performance
            resolve_time = time.time() - start_time
            self._log_access(name, "resolved", resolve_time)
            
            return result
            
        except Exception as e:
            self._log_access(name, "error", time.time() - start_time, str(e))
            log_debug(f"Failed to resolve {full_path}: {e}")
            raise AttributeError(f"'{self._module_path}' has no attribute '{name}'")
    
    def _resolve_symbol(self, package_name: str, symbol_name: str, full_path: str) -> Any:
        """Resolve a symbol from the CDN server."""
        try:
            # Get symbol metadata from server
            response = self._cdn_client._execute_request(
                package_name=package_name,
                function_name="__getattr__",
                serialized_args={"args": f'["{symbol_name}"]', "kwargs": "{}"}
            )
            
            if not response.get("success", False):
                raise AttributeError(f"Symbol '{symbol_name}' not found")
            
            symbol_info = response.get("result", {})
            symbol_type = symbol_info.get("type", "unknown")
            
            # Create appropriate proxy based on type
            if symbol_type == "module":
                sub_proxy = HybridCDNProxy(self._cdn_client, full_path, self)
                # Register the sub-module in sys.modules for natural imports
                module_name = f"cdn.{full_path}" if not full_path.startswith("cdn") else full_path
                sys.modules[module_name] = sub_proxy
                log_debug(f"Registered sub-module {module_name} in sys.modules")
                return sub_proxy
            elif symbol_type == "class":
                return CDNClassProxy(self._cdn_client, package_name, symbol_name, full_path)
            elif symbol_type == "function":
                return CDNFunctionProxy(self._cdn_client, package_name, symbol_name, full_path)
            else:
                return CDNCallableProxy(self._cdn_client, package_name, symbol_name, full_path)
                
        except Exception as e:
            # If direct resolution fails, try heuristic-based resolution
            log_debug(f"Server resolution failed for {symbol_name}, using heuristics: {e}")
            
            # For root-level package names (like 'openai', 'numpy'), create sub-modules
            # For nested symbols (like 'OpenAI', 'sqrt'), use type heuristics
            if self._module_path == "cdn" or self._module_path == "":
                # This is a top-level package access (e.g., cdn.openai)
                sub_proxy = HybridCDNProxy(self._cdn_client, full_path, self)
                # Register the sub-module in sys.modules for natural imports
                module_name = f"cdn.{full_path}" if not full_path.startswith("cdn") else full_path
                sys.modules[module_name] = sub_proxy
                log_debug(f"Registered top-level package {module_name} in sys.modules")
                return sub_proxy
            else:
                # This is accessing a symbol within a package (e.g., openai.OpenAI)
                if symbol_name[0].isupper():
                    # Likely a class (e.g., OpenAI, Client, API)
                    log_debug(f"Creating CDNClassProxy for {symbol_name} (uppercase heuristic)")
                    return CDNClassProxy(self._cdn_client, package_name, symbol_name, full_path)
                elif symbol_name.islower() and not symbol_name.startswith('_'):
                    # Likely a function
                    log_debug(f"Creating CDNFunctionProxy for {symbol_name} (lowercase heuristic)")
                    return CDNFunctionProxy(self._cdn_client, package_name, symbol_name, full_path)
                else:
                    # Create a callable proxy as fallback
                    return CDNCallableProxy(self._cdn_client, package_name, symbol_name, full_path)
    
    def _log_access(self, name: str, action: str, duration: float = 0, error: str = None):
        """Log access for profiling and debugging."""
        log_entry = {
            "timestamp": time.time(),
            "module_path": self._module_path,
            "symbol": name,
            "action": action,
            "duration": duration
        }
        if error:
            log_entry["error"] = error
        
        self._access_log.append(log_entry)
        
        # Update profile data
        if name not in self._profile_data:
            self._profile_data[name] = {"calls": 0, "total_time": 0, "errors": 0}
        
        self._profile_data[name]["calls"] += 1
        self._profile_data[name]["total_time"] += duration
        if error:
            self._profile_data[name]["errors"] += 1
    
    def __dir__(self) -> List[str]:
        """Return available attributes."""
        # Combine cached attributes with smart discovery
        attrs = list(self._cached_attrs.keys())
        
        # Add common Python package attributes
        if not self._module_path or self._module_path == "cdn":
            attrs.extend(["openai", "numpy", "pandas", "requests", "fastapi"])
        
        # Add special methods
        attrs.extend(["reload", "profile", "alias", "dev_mode", "list_packages", "describe"])
        
        return sorted(set(attrs))
    
    # ========== Smart Enhancement Methods ==========
    
    def reload(self, package_name: str = None):
        """Force reload a package or all packages."""
        if package_name:
            # Clear specific package from cache
            keys_to_remove = [k for k in self._cached_attrs.keys() 
                            if k == package_name or k.startswith(f"{package_name}.")]
            for key in keys_to_remove:
                del self._cached_attrs[key]
            log_debug(f"Reloaded package: {package_name}")
            return f"✅ Reloaded {package_name}"
        else:
            # Clear all cache
            self._cached_attrs.clear()
            log_debug("Reloaded all packages")
            return "✅ Reloaded all packages"
    
    def alias(self, original_name: str, alias_name: str):
        """Create an alias for a package."""
        self._aliases[alias_name] = original_name
        log_debug(f"Created alias: {alias_name} -> {original_name}")
        return f"✅ Created alias: {alias_name} -> {original_name}"
    
    def profile(self, package_name: str = None) -> Dict[str, Any]:
        """Get profiling information."""
        if package_name and package_name in self._profile_data:
            return {package_name: self._profile_data[package_name]}
        return dict(self._profile_data)
    
    def dev_mode(self, enabled: bool = True, local_packages: Dict[str, Any] = None):
        """Enable/disable development mode with local fallbacks."""
        object.__setattr__(self, '_dev_mode', enabled)
        if local_packages:
            object.__setattr__(self, '_local_fallbacks', local_packages)
        
        status = "enabled" if enabled else "disabled"
        log_debug(f"Dev mode {status}")
        return f"✅ Dev mode {status}"
    
    def list_packages(self) -> List[str]:
        """List available packages on the CDN."""
        try:
            response = self._cdn_client._execute_request(
                package_name="__system__",
                function_name="list_packages",
                serialized_args={"args": "[]", "kwargs": "{}"}
            )
            if response.get("success", False):
                return response.get("result", [])
        except Exception:
            pass
        
        # Fallback to cached packages
        return list(set(k.split('.')[0] for k in self._cached_attrs.keys() if '.' not in k))
    
    def describe(self, symbol_path: str) -> Dict[str, Any]:
        """Get detailed information about a symbol."""
        try:
            parts = symbol_path.split('.')
            package_name = parts[0]
            symbol_name = '.'.join(parts[1:]) if len(parts) > 1 else "__module__"
            
            response = self._cdn_client._execute_request(
                package_name=package_name,
                function_name="__describe__",
                serialized_args={"args": f'["{symbol_name}"]', "kwargs": "{}"}
            )
            
            if response.get("success", False):
                return response.get("result", {})
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "Symbol not found"}
    
    def _introspect(self, symbol_path: str) -> Dict[str, Any]:
        """Development-only introspection."""
        return {
            "path": symbol_path,
            "cached": symbol_path in self._cached_attrs,
            "type": type(self._cached_attrs.get(symbol_path, None)).__name__,
            "access_count": self._profile_data.get(symbol_path, {}).get("calls", 0),
            "avg_time": (self._profile_data.get(symbol_path, {}).get("total_time", 0) / 
                        max(1, self._profile_data.get(symbol_path, {}).get("calls", 1)))
        }
    
    def __repr__(self):
        if self._module_path:
            return f"<HybridCDNModule '{self._module_path}' from '{self._cdn_client.url}'>"
        else:
            return f"<HybridCDNRoot from '{self._cdn_client.url}'>"


class CDNFunctionProxy:
    """Enhanced proxy for remote CDN functions."""
    
    def __init__(self, cdn_client, package_name: str, function_name: str, full_path: str):
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._function_name = function_name
        self._full_path = full_path
        self._call_count = 0
        self._total_time = 0
        
        # Inject Python function metadata
        self.__name__ = function_name
        self.__qualname__ = full_path
        self.__module__ = package_name
    
    def __call__(self, *args, **kwargs):
        """Execute the remote function with timing."""
        start_time = time.time()
        self._call_count += 1
        
        try:
            result = self._cdn_client.call_function(
                self._package_name,
                self._function_name,
                args,
                kwargs
            )
            self._total_time += time.time() - start_time
            return result
        except Exception as e:
            self._total_time += time.time() - start_time
            raise e
    
    @property
    def __doc__(self):
        """Dynamically fetch docstring from server."""
        try:
            response = self._cdn_client._execute_request(
                package_name=self._package_name,
                function_name="__doc__",
                serialized_args={"args": f'["{self._function_name}"]', "kwargs": "{}"}
            )
            if response.get("success", False):
                return response.get("result", "")
        except Exception:
            pass
        return f"Remote function {self._full_path}"
    
    def __repr__(self):
        avg_time = self._total_time / max(1, self._call_count)
        return f"<CDNFunction '{self._full_path}' calls={self._call_count} avg={avg_time:.3f}s>"


class CDNClassProxy:
    """Enhanced proxy for remote CDN classes."""
    
    def __init__(self, cdn_client, package_name: str, class_name: str, full_path: str):
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._class_name = class_name
        self._full_path = full_path
        self._instance_count = 0
        
        # Inject Python class metadata
        self.__name__ = class_name
        self.__qualname__ = full_path
        self.__module__ = package_name
    
    def __call__(self, *args, **kwargs):
        """Create an enhanced instance of the remote class."""
        self._instance_count += 1
        return CDNInstanceProxy(
            self._cdn_client,
            self._package_name,
            self._class_name,
            self._full_path,
            args,
            kwargs,
            instance_id=f"{self._full_path}_{self._instance_count}"
        )
    
    def __getattr__(self, name: str):
        """Access class methods/attributes."""
        if name.startswith('_'):
            raise AttributeError(f"'{self._class_name}' has no attribute '{name}'")
        
        return CDNCallableProxy(
            self._cdn_client,
            self._package_name,
            f"{self._class_name}.{name}",
            f"{self._full_path}.{name}"
        )
    
    @property
    def __doc__(self):
        """Dynamically fetch class docstring."""
        try:
            response = self._cdn_client._execute_request(
                package_name=self._package_name,
                function_name="__doc__",
                serialized_args={"args": f'["{self._class_name}"]', "kwargs": "{}"}
            )
            if response.get("success", False):
                return response.get("result", "")
        except Exception:
            pass
        return f"Remote class {self._full_path}"
    
    def __repr__(self):
        return f"<CDNClass '{self._full_path}' instances={self._instance_count}>"


class CDNInstanceProxy:
    """Enhanced proxy for instances of remote CDN classes."""
    
    def __init__(self, cdn_client, package_name: str, class_name: str, full_path: str, 
                 init_args: tuple, init_kwargs: dict, instance_id: str):
        object.__setattr__(self, '_cdn_client', cdn_client)
        object.__setattr__(self, '_package_name', package_name)
        object.__setattr__(self, '_class_name', class_name)
        object.__setattr__(self, '_full_path', full_path)
        object.__setattr__(self, '_init_args', init_args)
        object.__setattr__(self, '_init_kwargs', init_kwargs)
        object.__setattr__(self, '_instance_id', instance_id)
        object.__setattr__(self, '_method_cache', {})
        
        # Create the instance on the server
        self._create_instance()
    
    def _create_instance(self):
        """Create the instance on the remote server."""
        try:
            response = self._cdn_client.call_function(
                self._package_name,
                f"{self._class_name}.__init__",
                self._init_args,
                self._init_kwargs
            )
            log_debug(f"Created remote instance: {self._instance_id}")
        except Exception as e:
            raise PyCDNRemoteError(
                f"Failed to create instance of {self._class_name}: {e}",
                package_name=self._package_name
            )
    
    def __getattr__(self, name: str):
        """Access instance methods/attributes with caching."""
        if name.startswith('_'):
            raise AttributeError(f"'{self._class_name}' instance has no attribute '{name}'")
        
        # Check method cache
        if name in self._method_cache:
            return self._method_cache[name]
        
        # Create method proxy
        method_proxy = CDNMethodProxy(
            self._cdn_client,
            self._package_name,
            self._class_name,
            name,
            self._instance_id
        )
        
        # Cache it
        self._method_cache[name] = method_proxy
        return method_proxy
    
    def __repr__(self):
        return f"<CDNInstance '{self._full_path}' id={self._instance_id}>"


class CDNMethodProxy:
    """Enhanced proxy for remote instance methods."""
    
    def __init__(self, cdn_client, package_name: str, class_name: str, 
                 method_name: str, instance_id: str):
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._class_name = class_name
        self._method_name = method_name
        self._instance_id = instance_id
        self._call_count = 0
    
    def __call__(self, *args, **kwargs):
        """Execute the remote method."""
        self._call_count += 1
        return self._cdn_client.call_function(
            self._package_name,
            f"{self._class_name}.{self._method_name}",
            args,
            kwargs,
            instance_id=self._instance_id
        )
    
    def __repr__(self):
        return f"<CDNMethod '{self._class_name}.{self._method_name}' calls={self._call_count}>"


class CDNCallableProxy:
    """Enhanced proxy for generic CDN callables."""
    
    def __init__(self, cdn_client, package_name: str, callable_name: str, full_path: str):
        self._cdn_client = cdn_client
        self._package_name = package_name
        self._callable_name = callable_name
        self._full_path = full_path
        self._call_count = 0
    
    def __call__(self, *args, **kwargs):
        """Execute the remote callable."""
        self._call_count += 1
        return self._cdn_client.call_function(
            self._package_name,
            self._callable_name,
            args,
            kwargs
        )
    
    def __repr__(self):
        return f"<CDNCallable '{self._full_path}' calls={self._call_count}>"


class HybridMetaPathFinder(importlib.abc.MetaPathFinder):
    """
    Meta path finder that handles 'cdn' imports for the hybrid system.
    """
    
    def __init__(self):
        self._cdn_roots = {}  # prefix -> HybridCDNProxy
        self._lock = threading.Lock()
    
    def find_spec(self, fullname: str, path: Optional[List[str]], target=None):
        """Find module spec for cdn imports."""
        # Only handle 'cdn' and 'cdn.*' imports
        if not (fullname == 'cdn' or fullname.startswith('cdn.')):
            return None
        
        with self._lock:
            # Check if we have a registered CDN root for 'cdn'
            if 'cdn' in self._cdn_roots:
                log_debug(f"Creating spec for {fullname}")
                
                loader = HybridModuleLoader(self._cdn_roots['cdn'], fullname)
                spec = importlib.machinery.ModuleSpec(fullname, loader)
                return spec
        
        return None
    
    def register_cdn_root(self, prefix: str, cdn_root: HybridCDNProxy) -> None:
        """Register a CDN root for imports."""
        with self._lock:
            self._cdn_roots[prefix] = cdn_root
            log_debug(f"Registered CDN root for prefix '{prefix}'")
    
    def unregister_cdn_root(self, prefix: str) -> None:
        """Unregister a CDN root."""
        with self._lock:
            if prefix in self._cdn_roots:
                del self._cdn_roots[prefix]
                log_debug(f"Unregistered CDN root for prefix '{prefix}'")


class HybridModuleLoader(importlib.abc.Loader):
    """
    Module loader for the hybrid system.
    """
    
    def __init__(self, cdn_root: HybridCDNProxy, module_name: str):
        self._cdn_root = cdn_root
        self._module_name = module_name
    
    def create_module(self, spec):
        """Create module - return None to use default creation."""
        return None
    
    def exec_module(self, module):
        """Execute module by setting up the hybrid proxy."""
        if self._module_name == 'cdn':
            # For 'import cdn', make the module act like the root proxy
            # Copy all attributes and methods from the CDN root
            module.__dict__.update(self._cdn_root.__dict__)
            
            # Make sure all public methods are accessible
            for attr_name in dir(self._cdn_root):
                if not attr_name.startswith('_'):
                    try:
                        setattr(module, attr_name, getattr(self._cdn_root, attr_name))
                    except AttributeError:
                        pass
                        
            # Set special attributes for package behavior
            module.__path__ = []  # Mark as package
            module.__package__ = 'cdn'
            
        else:
            # For 'from cdn.package import Symbol', get the package proxy and resolve all symbols
            package_path = self._module_name[4:]  # Remove 'cdn.' prefix
            
            try:
                # Navigate to the package proxy through the CDN root
                package_proxy = self._cdn_root
                for part in package_path.split('.'):
                    package_proxy = getattr(package_proxy, part)
                
                # Get all attributes from the package proxy
                # This ensures 'from cdn.openai import OpenAI' gets the actual OpenAI class
                package_dir = dir(package_proxy)
                for attr_name in package_dir:
                    if not attr_name.startswith('_'):
                        try:
                            # Resolve each attribute to get the actual symbol (class/function/etc)
                            attr_value = getattr(package_proxy, attr_name)
                            setattr(module, attr_name, attr_value)
                        except AttributeError:
                            pass
                
                # Also add common symbols that might not be in dir()
                common_symbols = ['OpenAI', 'Client', 'API', '__version__', '__all__']
                for symbol in common_symbols:
                    if not hasattr(module, symbol):
                        try:
                            symbol_value = getattr(package_proxy, symbol)
                            setattr(module, symbol, symbol_value)
                        except AttributeError:
                            pass
                            
                # Set module metadata
                module.__package__ = 'cdn'
                module.__path__ = []
                
            except AttributeError as e:
                # If we can't find the package, create a stub
                log_debug(f"Package {package_path} not found, creating stub: {e}")
                module.__package__ = 'cdn'
                module.__path__ = []


# Global finder instance
_hybrid_finder = None
_finder_lock = threading.Lock()


def install_hybrid_finder() -> None:
    """Install the hybrid meta path finder."""
    global _hybrid_finder
    
    with _finder_lock:
        if _hybrid_finder is None:
            _hybrid_finder = HybridMetaPathFinder()
            sys.meta_path.insert(0, _hybrid_finder)
            log_debug("Installed hybrid meta path finder")


def uninstall_hybrid_finder() -> None:
    """Uninstall the hybrid meta path finder."""
    global _hybrid_finder
    
    with _finder_lock:
        if _hybrid_finder and _hybrid_finder in sys.meta_path:
            sys.meta_path.remove(_hybrid_finder)
            _hybrid_finder = None
            log_debug("Uninstalled hybrid meta path finder")


def register_hybrid_cdn(cdn_client, prefix: str = "cdn") -> HybridCDNProxy:
    """
    Register a CDN client for hybrid import/access.
    
    Returns:
        HybridCDNProxy that supports both classic and import syntax
    """
    # Ensure finder is installed
    install_hybrid_finder()
    
    # Create hybrid root proxy
    cdn_root = HybridCDNProxy(cdn_client, prefix)
    
    # Set the prefix attribute so it can be accessed
    object.__setattr__(cdn_root, '_prefix', prefix)
    
    # Register with finder
    global _hybrid_finder
    if _hybrid_finder:
        _hybrid_finder.register_cdn_root(prefix, cdn_root)
    
    # Also register in sys.modules for direct access
    sys.modules[prefix] = cdn_root
    
    log_debug(f"Registered hybrid CDN with prefix '{prefix}'")
    return cdn_root


def unregister_hybrid_cdn(prefix: str = "cdn") -> None:
    """Unregister a hybrid CDN."""
    global _hybrid_finder
    
    if _hybrid_finder:
        _hybrid_finder.unregister_cdn_root(prefix)
    
    # Remove from sys.modules
    if prefix in sys.modules:
        del sys.modules[prefix]
    
    log_debug(f"Unregistered hybrid CDN with prefix '{prefix}'")


def get_hybrid_mappings() -> Dict[str, str]:
    """Get current hybrid CDN mappings."""
    global _hybrid_finder
    if _hybrid_finder:
        return {prefix: str(root._cdn_client.url) 
                for prefix, root in _hybrid_finder._cdn_roots.items()}
    return {}


def clear_hybrid_mappings() -> None:
    """Clear all hybrid CDN mappings."""
    global _hybrid_finder
    if _hybrid_finder:
        prefixes = list(_hybrid_finder._cdn_roots.keys())
        for prefix in prefixes:
            unregister_hybrid_cdn(prefix)