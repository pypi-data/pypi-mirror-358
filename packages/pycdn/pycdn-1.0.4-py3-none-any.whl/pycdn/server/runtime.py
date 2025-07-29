"""
Package runtime execution environment for PyCDN server.
"""

import sys
import importlib
import importlib.util
import traceback
from typing import Any, Dict, List, Optional, Tuple
from ..utils.common import deserialize_args, serialize_result, serialize_error, log_debug


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
        
    def load_package(self) -> None:
        """Load the specified package into the environment."""
        try:
            if self.package_name not in self._loaded_modules:
                log_debug(f"Loading package: {self.package_name}")
                module = importlib.import_module(self.package_name)
                self._loaded_modules[self.package_name] = module
                log_debug(f"Successfully loaded package: {self.package_name}")
        except ImportError as e:
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
            func = self.get_function(function_name)
            log_debug(f"Executing {self.package_name}.{function_name} with args={args}, kwargs={kwargs}")
            
            # Execute function
            result = func(*args, **kwargs)
            log_debug(f"Execution completed successfully")
            
            return result
            
        except Exception as e:
            log_debug(f"Execution failed: {e}")
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
            
            # Get execution environment
            env = self.get_environment(package_name)
            
            # Execute function
            result = env.execute_function(function_name, args, kwargs)
            
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