"""
Package runtime execution environment for PyCDN server.
"""

import sys
import importlib
import importlib.util
import traceback
import subprocess
import time
import glob
import site
from typing import Any, Dict, List, Optional, Tuple
from ..utils.common import deserialize_args, serialize_result, serialize_error, log_debug
from ..utils.encryption import get_global_encryption


def install_package(package_name: str) -> bool:
    """
    Install a package dynamically using multiple methods.
    
    Args:
        package_name: Name of the package to install
        
    Returns:
        True if installation successful, False otherwise
    """
    try:
        log_debug(f"Attempting to install package: {package_name}")
        
        # Method 1: Try using pip programmatically first (more reliable in cloud environments)
        try:
            import pip
            if hasattr(pip, 'main'):
                # Older pip versions
                result = pip.main(['install', package_name])
                if result == 0:
                    log_debug(f"Successfully installed {package_name} using pip.main")
                    return True
            else:
                # Newer pip versions don't have main, fall through to subprocess
                pass
        except Exception as pip_error:
            log_debug(f"pip.main method failed: {pip_error}")
        
        # Method 2: Try using subprocess (standard method)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name, "--user", "--quiet"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False
            )
            
            if result.returncode == 0:
                log_debug(f"Successfully installed {package_name} using subprocess")
                return True
            else:
                log_debug(f"Subprocess pip install failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            log_debug(f"Package installation timed out for {package_name}")
        except Exception as subprocess_error:
            log_debug(f"Subprocess method failed: {subprocess_error}")
        
        # Method 3: Try using importlib and pip's internal API (for restrictive environments)
        try:
            import importlib.util
            spec = importlib.util.find_spec('pip')
            if spec is not None:
                pip_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(pip_module)
                
                # Try using pip's internal API
                if hasattr(pip_module, '_internal'):
                    from pip._internal import main as pip_main
                    result = pip_main(['install', package_name, '--user', '--quiet'])
                    if result == 0:
                        log_debug(f"Successfully installed {package_name} using pip._internal")
                        return True
        except Exception as internal_error:
            log_debug(f"pip._internal method failed: {internal_error}")
        
        # Method 4: Try alternative installation using ensurepip + subprocess with different flags
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--target", "/tmp", package_name],
                capture_output=True,
                text=True,
                timeout=300,
                check=False
            )
            
            if result.returncode == 0:
                # Add /tmp to sys.path temporarily for this package
                if "/tmp" not in sys.path:
                    sys.path.insert(0, "/tmp")
                log_debug(f"Successfully installed {package_name} to /tmp")
                return True
        except Exception as target_error:
            log_debug(f"Target installation method failed: {target_error}")
        
        log_debug(f"All installation methods failed for {package_name}")
        return False
        
    except Exception as e:
        log_debug(f"Error installing {package_name}: {e}")
        return False


class ExecutionEnvironment:
    """
    Sandboxed execution environment for package functions.
    """
    
    def __init__(self, package_name: str, security_level: str = "standard"):
        """
        Initialize execution environment.
        
        Args:
            package_name: Name of the package to execute
            security_level: Security level (basic, standard, strict)
        """
        self.package_name = package_name
        self.security_level = security_level
        self._loaded_modules = {}
        self._execution_cache = {}
        
        # Auto-install if package not found
        self.auto_install = True
        
    def load_package(self) -> None:
        """Load the specified package into the environment."""
        if self.package_name in self._loaded_modules:
            return
            
        try:
            log_debug(f"Loading package: {self.package_name}")
            module = importlib.import_module(self.package_name)
            self._loaded_modules[self.package_name] = module
            log_debug(f"Successfully loaded package: {self.package_name}")
        except ImportError as e:
            if self.auto_install:
                log_debug(f"Package {self.package_name} not found, attempting auto-install...")
                log_debug(f"Original import error: {e}")
                
                # Check if it's a submodule import issue
                main_package = self.package_name.split('.')[0]
                
                # Try installing the main package first
                package_to_install = main_package if main_package != self.package_name else self.package_name
                
                if install_package(package_to_install):
                    # Try importing again after installation
                    try:
                        # Clear import cache to ensure fresh import
                        modules_to_clear = [key for key in sys.modules.keys() 
                                          if key.startswith(self.package_name) or key.startswith(main_package)]
                        for module_name in modules_to_clear:
                            if module_name in sys.modules:
                                del sys.modules[module_name]
                        
                        # Force reload of importlib caches
                        importlib.invalidate_caches()
                        
                        # Wait a moment for the installation to settle
                        time.sleep(0.5)
                            
                        module = importlib.import_module(self.package_name)
                        self._loaded_modules[self.package_name] = module
                        log_debug(f"Successfully loaded package after installation: {self.package_name}")
                        return
                    except ImportError as import_error:
                        log_debug(f"Failed to import after installation: {import_error}")
                        
                        # For cloud environments, try alternative import strategies
                        try:
                            # Method 1: Try finding the package in alternative locations
                            import site
                            site.main()  # Refresh site-packages
                            
                            # Method 2: Check if package exists in /tmp or user directory
                            import glob
                            potential_paths = [
                                "/tmp",
                                "/tmp/lib/python*/site-packages",
                                f"{sys.prefix}/lib/python*/site-packages",
                                f"{sys.prefix}/local/lib/python*/site-packages"
                            ]
                            
                            for path_pattern in potential_paths:
                                matching_paths = glob.glob(path_pattern)
                                for path in matching_paths:
                                    if path not in sys.path:
                                        sys.path.insert(0, path)
                                        log_debug(f"Added {path} to sys.path")
                            
                            # Try importing once more
                            importlib.invalidate_caches()
                            module = importlib.import_module(self.package_name)
                            self._loaded_modules[self.package_name] = module
                            log_debug(f"Successfully loaded package using alternative paths: {self.package_name}")
                            return
                            
                        except Exception as alt_error:
                            log_debug(f"Alternative import methods failed: {alt_error}")
                        
                        raise ImportError(f"Failed to load package {self.package_name} even after installation. "
                                        f"Original error: {e}. Post-install error: {import_error}")
                else:
                    raise ImportError(f"Failed to auto-install package {self.package_name}: {e}")
            else:
                raise ImportError(f"Failed to load package {self.package_name}: {e}")
    
    def get_function(self, function_name: str) -> Any:
        """
        Get function from loaded package.
        
        Args:
            function_name: Name of the function to retrieve
            
        Returns:
            Function object
        """
        if self.package_name not in self._loaded_modules:
            self.load_package()
            
        module = self._loaded_modules[self.package_name]
        
        # Handle nested attributes (e.g., "submodule.function")
        parts = function_name.split('.')
        obj = module
        
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise AttributeError(f"'{self.package_name}' has no attribute '{function_name}'")
        
        return obj
    
    def execute_function(self, function_name: str, args: tuple, kwargs: dict) -> Any:
        """
        Execute a function with given arguments.
        
        Args:
            function_name: Name of the function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Function execution result
        """
        try:
            # Handle special instance method calls
            if function_name == "__instance_call__":
                return self._execute_instance_method(args[0])  # args[0] contains the instance call data
            
            func = self.get_function(function_name)
            log_debug(f"Executing {self.package_name}.{function_name} with args={args}, kwargs={kwargs}")
            
            # Execute function
            result = func(*args, **kwargs)
            log_debug(f"Execution completed successfully")
            
            return result
            
        except Exception as e:
            log_debug(f"Execution failed: {e}")
            raise e
    
    def _execute_instance_method(self, call_data: dict) -> Any:
        """
        Execute an instance method call.
        
        Args:
            call_data: Dictionary containing instance creation and method call information
            
        Returns:
            Method execution result
        """
        try:
            # Get encryption handler
            encryption = get_global_encryption()
            
            # Extract call data
            class_name = call_data["class_name"]
            init_args = call_data["init_args"]
            init_kwargs = call_data["init_kwargs"]
            method_path = call_data["method_path"]
            method_args = call_data["method_args"]
            method_kwargs = call_data["method_kwargs"]
            
            # Automatically decrypt sensitive data
            decrypted_init_args, decrypted_init_kwargs = encryption.process_response_arguments(
                init_args, init_kwargs
            )
            decrypted_method_args, decrypted_method_kwargs = encryption.process_response_arguments(
                method_args, method_kwargs
            )
            
            log_debug(f"Executing instance method {class_name}.{method_path}")
            
            # Get the class from the module
            cls = self.get_function(class_name)
            
            # Create instance with decrypted arguments
            instance = cls(*decrypted_init_args, **decrypted_init_kwargs)
            log_debug(f"Created instance of {class_name}")
            
            # Navigate to the method using the method path
            method_parts = method_path.split('.')
            obj = instance
            
            for part in method_parts:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    raise AttributeError(f"'{class_name}' instance has no attribute '{part}'")
            
            # Execute the method with decrypted arguments
            if callable(obj):
                result = obj(*decrypted_method_args, **decrypted_method_kwargs)
                log_debug(f"Instance method execution completed successfully")
                return result
            else:
                # It's an attribute, not a method
                log_debug(f"Returning attribute value for {method_path}")
                return obj
                
        except Exception as e:
            log_debug(f"Instance method execution failed: {e}")
            raise e


class PackageRuntime:
    """
    Main runtime manager for package execution.
    """
    
    def __init__(self):
        """Initialize package runtime."""
        self.environments = {}
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "packages_loaded": 0
        }
    
    def get_environment(self, package_name: str) -> ExecutionEnvironment:
        """
        Get or create execution environment for package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            ExecutionEnvironment instance
        """
        if package_name not in self.environments:
            self.environments[package_name] = ExecutionEnvironment(package_name)
            self.execution_stats["packages_loaded"] += 1
            
        return self.environments[package_name]
    
    def execute_remote_function(self, package_name: str, function_name: str, 
                              serialized_args: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute a remote function call.
        
        Args:
            package_name: Name of the package
            function_name: Name of the function
            serialized_args: Serialized function arguments
            
        Returns:
            Serialized execution result
        """
        self.execution_stats["total_executions"] += 1
        
        try:
            # Deserialize arguments
            args, kwargs = deserialize_args(serialized_args)
            
            # Apply automatic decryption to sensitive data
            encryption = get_global_encryption()
            decrypted_args, decrypted_kwargs = encryption.process_response_arguments(args, kwargs)
            
            # Get execution environment
            env = self.get_environment(package_name)
            
            # Execute function with decrypted arguments
            result = env.execute_function(function_name, decrypted_args, decrypted_kwargs)
            
            # Serialize result
            serialized_result = serialize_result(result)
            
            self.execution_stats["successful_executions"] += 1
            return serialized_result
            
        except Exception as e:
            log_debug(f"Remote execution failed: {e}")
            self.execution_stats["failed_executions"] += 1
            return serialize_error(e)
    
    def get_package_info(self, package_name: str) -> Dict[str, Any]:
        """
        Get information about a loaded package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Package information dict
        """
        try:
            env = self.get_environment(package_name)
            env.load_package()
            
            module = env._loaded_modules[package_name]
            
            # Get package attributes
            attributes = []
            for name in dir(module):
                if not name.startswith('_'):
                    obj = getattr(module, name)
                    obj_type = type(obj).__name__
                    attributes.append({
                        "name": name,
                        "type": obj_type,
                        "callable": callable(obj)
                    })
            
            return {
                "package_name": package_name,
                "version": getattr(module, "__version__", "unknown"),
                "file": getattr(module, "__file__", "unknown"),
                "attributes": attributes,
                "loaded": True
            }
            
        except Exception as e:
            return {
                "package_name": package_name,
                "error": str(e),
                "loaded": False
            }
    
    def list_loaded_packages(self) -> List[str]:
        """
        List all loaded packages.
        
        Returns:
            List of package names
        """
        return list(self.environments.keys())
    
    def get_execution_stats(self) -> Dict[str, int]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary of execution statistics
        """
        return self.execution_stats.copy()
    
    def clear_cache(self, package_name: Optional[str] = None) -> None:
        """
        Clear package cache.
        
        Args:
            package_name: Specific package to clear, or None for all
        """
        if package_name:
            if package_name in self.environments:
                del self.environments[package_name]
        else:
            self.environments.clear()
            self.execution_stats["packages_loaded"] = 0 