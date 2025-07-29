"""
Common utility functions for PyCDN.
"""

import json
import pickle
import base64
import logging
from typing import Any, Dict, Optional, Union
import cloudpickle
from .encryption import get_global_encryption

# Global debug state
_debug_mode = False

def get_version() -> str:
    """Get PyCDN version string."""
    return "1.1.6"

def set_debug_mode(enabled: bool) -> None:
    """Enable or disable debug mode."""
    global _debug_mode
    _debug_mode = enabled
    
    # Configure logging
    if enabled:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("pycdn")
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return _debug_mode

def log_debug(message: str) -> None:
    """Log debug message if debug mode is enabled."""
    if _debug_mode:
        logger = logging.getLogger("pycdn")
        logger.debug(message)

def serialize_args(*args, **kwargs) -> Dict[str, str]:
    """
    Serialize function arguments for transmission to CDN server.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Dict containing serialized arguments
    """
    def _process_arg(arg):
        """Process individual argument, handling LazyInstance objects."""
        # Import here to avoid circular imports
        from pycdn.client.lazy_loader import LazyInstance
        
        if isinstance(arg, LazyInstance):
            # Convert LazyInstance to a serializable representation
            return {
                "_lazy_instance": True,
                "package_name": arg._package_name,
                "class_name": arg._class_name,
                "init_args": [_process_arg(a) for a in arg._init_args],
                "init_kwargs": {k: _process_arg(v) for k, v in arg._init_kwargs.items()}
            }
        elif isinstance(arg, (list, tuple)):
            return type(arg)([_process_arg(item) for item in arg])
        elif isinstance(arg, dict):
            return {k: _process_arg(v) for k, v in arg.items()}
        else:
            return arg
    
    try:
        # Process arguments to handle LazyInstance objects
        processed_args = tuple(_process_arg(arg) for arg in args)
        processed_kwargs = {k: _process_arg(v) for k, v in kwargs.items()}
        
        # Use cloudpickle for better serialization of complex objects
        serialized_args = base64.b64encode(cloudpickle.dumps(processed_args)).decode('utf-8')
        serialized_kwargs = base64.b64encode(cloudpickle.dumps(processed_kwargs)).decode('utf-8')
        
        return {
            "args": serialized_args,
            "kwargs": serialized_kwargs,
            "serialization_method": "cloudpickle"
        }
    except Exception as e:
        log_debug(f"Cloudpickle serialization failed: {e}, falling back to JSON")
        
        # Fallback to JSON for simple types
        try:
            # Process arguments again for JSON compatibility
            processed_args = tuple(_process_arg(arg) for arg in args)
            processed_kwargs = {k: _process_arg(v) for k, v in kwargs.items()}
            
            return {
                "args": json.dumps(processed_args),
                "kwargs": json.dumps(processed_kwargs),
                "serialization_method": "json"
            }
        except Exception as json_e:
            raise ValueError(f"Failed to serialize arguments: {json_e}")

def deserialize_args(serialized_data: Dict[str, str]) -> tuple:
    """
    Deserialize function arguments received from client.
    
    Args:
        serialized_data: Dict containing serialized arguments
        
    Returns:
        Tuple of (args, kwargs)
    """
    def _reconstruct_arg(arg):
        """Reconstruct argument, handling LazyInstance representations."""
        if isinstance(arg, dict) and arg.get("_lazy_instance"):
            # Reconstruct LazyInstance reference
            return {
                "_lazy_instance_ref": True,
                "package_name": arg["package_name"],
                "class_name": arg["class_name"],
                "init_args": [_reconstruct_arg(a) for a in arg["init_args"]],
                "init_kwargs": {k: _reconstruct_arg(v) for k, v in arg["init_kwargs"].items()}
            }
        elif isinstance(arg, (list, tuple)):
            return type(arg)([_reconstruct_arg(item) for item in arg])
        elif isinstance(arg, dict):
            return {k: _reconstruct_arg(v) for k, v in arg.items()}
        else:
            return arg
    
    method = serialized_data.get("serialization_method", "json")
    
    try:
        if method == "cloudpickle":
            args = cloudpickle.loads(base64.b64decode(serialized_data["args"]))
            kwargs = cloudpickle.loads(base64.b64decode(serialized_data["kwargs"]))
        else:
            args = json.loads(serialized_data["args"])
            kwargs = json.loads(serialized_data["kwargs"])
        
        # Reconstruct LazyInstance references
        args = tuple(_reconstruct_arg(arg) for arg in args)
        kwargs = {k: _reconstruct_arg(v) for k, v in kwargs.items()}
            
        return args, kwargs
    except Exception as e:
        raise ValueError(f"Failed to deserialize arguments: {e}")

def serialize_result(result: Any) -> Dict[str, str]:
    """
    Serialize function result for transmission back to client.
    
    Args:
        result: Function execution result
        
    Returns:
        Dict containing serialized result
    """
    def convert_to_basic_types(obj):
        """Convert complex objects to basic Python types for safe serialization."""
        try:
            # Handle common object types that might not deserialize well
            if hasattr(obj, '__dict__'):
                # Convert objects with __dict__ to dictionaries
                if hasattr(obj, 'model_dump'):
                    # Pydantic models (like OpenAI responses)
                    result_dict = obj.model_dump()
                    # Add type information so DictWrapper can restore object interface
                    result_dict['__type__'] = type(obj).__name__
                    result_dict['__module__'] = getattr(type(obj), '__module__', 'unknown')
                    # Recursively process nested objects
                    for key, value in result_dict.items():
                        if not key.startswith('__'):
                            result_dict[key] = convert_to_basic_types(value)
                    return result_dict
                elif hasattr(obj, 'dict'):
                    # Objects with dict() method
                    result_dict = obj.dict()
                    # Add type information so DictWrapper can restore object interface
                    result_dict['__type__'] = type(obj).__name__
                    result_dict['__module__'] = getattr(type(obj), '__module__', 'unknown')
                    # Recursively process nested objects
                    for key, value in result_dict.items():
                        if not key.startswith('__'):
                            result_dict[key] = convert_to_basic_types(value)
                    return result_dict
                elif hasattr(obj, 'to_dict'):
                    # Objects with to_dict() method
                    result_dict = obj.to_dict()
                    # Add type information so DictWrapper can restore object interface
                    result_dict['__type__'] = type(obj).__name__
                    result_dict['__module__'] = getattr(type(obj), '__module__', 'unknown')
                    # Recursively process nested objects
                    for key, value in result_dict.items():
                        if not key.startswith('__'):
                            result_dict[key] = convert_to_basic_types(value)
                    return result_dict
                else:
                    # Generic object conversion
                    result_dict = {}
                    for key, value in obj.__dict__.items():
                        if not key.startswith('_'):  # Skip private attributes
                            try:
                                result_dict[key] = convert_to_basic_types(value)
                            except:
                                result_dict[key] = str(value)
                    
                    # Add type information for debugging
                    result_dict['__type__'] = type(obj).__name__
                    result_dict['__module__'] = getattr(type(obj), '__module__', 'unknown')
                    return result_dict
            
            # Handle sequences
            elif isinstance(obj, (list, tuple)):
                return [convert_to_basic_types(item) for item in obj]
            
            # Handle dictionaries
            elif isinstance(obj, dict):
                return {str(k): convert_to_basic_types(v) for k, v in obj.items()}
            
            # Basic types that are safe to serialize
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            
            # For anything else, convert to string
            else:
                return str(obj)
                
        except Exception as e:
            log_debug(f"Error converting object to basic types: {e}")
            return str(obj)
    
    try:
        # First try to convert to basic types for safer deserialization
        converted_result = convert_to_basic_types(result)
        
        # Try JSON serialization first (safest)
        try:
            json.dumps(converted_result)  # Test if it's JSON serializable
            return {
                "result": json.dumps(converted_result),
                "serialization_method": "json",
                "success": True
            }
        except:
            # If JSON fails, try cloudpickle on the converted result
            try:
                serialized_result = base64.b64encode(cloudpickle.dumps(converted_result)).decode('utf-8')
                return {
                    "result": serialized_result,
                    "serialization_method": "cloudpickle",
                    "success": True
                }
            except Exception as e:
                log_debug(f"Cloudpickle serialization failed: {e}, falling back to string")
                # Final fallback to string
                return {
                    "result": str(converted_result),
                    "serialization_method": "string",
                    "success": True
                }
                
    except Exception as e:
        log_debug(f"Result serialization failed: {e}, using string fallback")
        
        # Final fallback - convert to string
        try:
            return {
                "result": str(result),
                "serialization_method": "string",
                "success": True
            }
        except Exception as final_e:
            return {
                "result": f"<Serialization Error: {final_e}>",
                "serialization_method": "string",
                "success": True
            }

def deserialize_result(serialized_data: Dict[str, Any]) -> Any:
    """
    Deserialize function result received from server.
    
    Args:
        serialized_data: Dict containing serialized result
        
    Returns:
        Deserialized result with smart wrapping for converted objects
    """
    if not serialized_data.get("success", True):
        error = serialized_data.get("error", "Unknown error")
        raise RuntimeError(f"Remote execution failed: {error}")

    method = serialized_data.get("serialization_method", "json")
    result_data = serialized_data["result"]
    
    def wrap_converted_objects(obj):
        """
        Recursively wrap dictionaries that were converted from objects 
        to restore object-like attribute access.
        """
        if isinstance(obj, dict):
            # If this dict has __type__ field, it was converted from an object
            if '__type__' in obj:
                return DictWrapper(obj)
            else:
                # Regular dict - recursively process values
                return {k: wrap_converted_objects(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # Process list items
            return [wrap_converted_objects(item) for item in obj]
        else:
            # Basic type, return as-is
            return obj
    
    try:
        if method == "cloudpickle":
            result = cloudpickle.loads(base64.b64decode(result_data))
        elif method == "json":
            result = json.loads(result_data)
        else:
            # String fallback
            result = result_data
        
        # Apply smart wrapping to restore object interfaces
        return wrap_converted_objects(result)
        
    except Exception as e:
        raise ValueError(f"Failed to deserialize result: {e}")

def serialize_error(error: Exception) -> Dict[str, str]:
    """
    Serialize an error for transmission.
    
    Args:
        error: Exception to serialize
        
    Returns:
        Dict containing error information
    """
    return {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "serialization_method": "error"
    }

def validate_package_name(package_name: str) -> bool:
    """
    Validate package name format.
    
    Args:
        package_name: Package name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not package_name:
        return False
    
    # Basic validation - can be enhanced
    return package_name.replace("_", "").replace("-", "").replace(".", "").isalnum()

def format_size(size_bytes: int) -> str:
    """
    Format size in bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

def parse_size(size_str: str) -> int:
    """
    Parse size string to bytes.
    
    Args:
        size_str: Size string like "100MB"
        
    Returns:
        Size in bytes
    """
    size_str = size_str.upper().strip()
    
    if size_str.endswith('B'):
        size_str = size_str[:-1]
    
    multipliers = {
        'K': 1024,
        'M': 1024 ** 2,
        'G': 1024 ** 3,
        'T': 1024 ** 4
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            return int(float(size_str[:-1]) * multiplier)
    
    return int(size_str)


# Aliases for transport functions (used by client code)
def serialize_for_transport(data: Any) -> Any:
    """
    Serialize data for transport - alias for serialize_result.
    """
    if isinstance(data, (tuple, list)):
        # For args/kwargs tuples
        return base64.b64encode(cloudpickle.dumps(data)).decode('utf-8')
    else:
        # For single values
        result = serialize_result(data)
        return result.get("result")


def deserialize_from_transport(data: Any) -> Any:
    """
    Deserialize data from transport - alias for deserialize_result.
    """
    if isinstance(data, str):
        # Direct cloudpickle data
        try:
            result = cloudpickle.loads(base64.b64decode(data))
        except:
            # Fallback to JSON
            try:
                result = json.loads(data)
            except:
                result = data
    elif isinstance(data, dict) and "result" in data:
        # Structured result format
        return deserialize_result(data)
    else:
        result = data
    
    # Apply DictWrapper wrapping for consistent behavior
    def wrap_converted_objects(obj):
        """
        Recursively wrap dictionaries that were converted from objects 
        to restore object-like attribute access.
        """
        if isinstance(obj, dict):
            # If this dict has __type__ field, it was converted from an object
            if '__type__' in obj:
                return DictWrapper(obj)
            else:
                # Regular dict - recursively process values
                return {k: wrap_converted_objects(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # Process list items
            return [wrap_converted_objects(item) for item in obj]
        else:
            # Basic type, return as-is
            return obj
    
    return wrap_converted_objects(result)


def parse_cache_size(size_str: Union[str, int]) -> int:
    """
    Parse cache size - alias for parse_size.
    """
    return parse_size(size_str)


class DictWrapper:
    """
    A wrapper that makes dictionaries behave like objects with attribute access.
    This allows converted objects to maintain their original interface.
    """
    
    def __init__(self, data: dict):
        # Store the data in __dict__ to enable attribute access
        if isinstance(data, dict):
            # Convert nested dictionaries to DictWrappers as well
            wrapped_data = {}
            for key, value in data.items():
                if isinstance(value, dict) and not key.startswith('__'):
                    wrapped_data[key] = DictWrapper(value)
                elif isinstance(value, list):
                    wrapped_data[key] = [
                        DictWrapper(item) if isinstance(item, dict) else item 
                        for item in value
                    ]
                else:
                    wrapped_data[key] = value
            self.__dict__.update(wrapped_data)
        else:
            # Not a dict, store as-is
            self.__dict__['_data'] = data
    
    def __getitem__(self, key):
        """Support dictionary-style access."""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)
    
    def __contains__(self, key):
        """Support 'in' operator."""
        return hasattr(self, key)
    
    def get(self, key, default=None):
        """Support dict.get() method."""
        return getattr(self, key, default)
    
    def keys(self):
        """Support dict.keys() method."""
        return [k for k in self.__dict__.keys() if not k.startswith('_')]
    
    def values(self):
        """Support dict.values() method."""
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]
    
    def items(self):
        """Support dict.items() method."""
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]
    
    def __repr__(self):
        type_info = getattr(self, '__type__', 'DictWrapper')
        module_info = getattr(self, '__module__', '')
        if module_info:
            return f"<{module_info}.{type_info} (via PyCDN)>"
        return f"<{type_info} (via PyCDN)>"
    
    def __str__(self):
        return self.__repr__() 