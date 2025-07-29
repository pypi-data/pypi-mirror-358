"""
Common utility functions for PyCDN.
"""

import json
import pickle
import base64
import logging
from typing import Any, Dict, Optional, Union
import cloudpickle

# Global debug state
_debug_mode = False

def get_version() -> str:
    """Get PyCDN version."""
    return "0.1.0"

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
    try:
        # Use cloudpickle for better serialization of complex objects
        serialized_args = base64.b64encode(cloudpickle.dumps(args)).decode('utf-8')
        serialized_kwargs = base64.b64encode(cloudpickle.dumps(kwargs)).decode('utf-8')
        
        return {
            "args": serialized_args,
            "kwargs": serialized_kwargs,
            "serialization_method": "cloudpickle"
        }
    except Exception as e:
        log_debug(f"Cloudpickle serialization failed: {e}, falling back to JSON")
        
        # Fallback to JSON for simple types
        try:
            return {
                "args": json.dumps(args),
                "kwargs": json.dumps(kwargs),
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
    method = serialized_data.get("serialization_method", "json")
    
    try:
        if method == "cloudpickle":
            args = cloudpickle.loads(base64.b64decode(serialized_data["args"]))
            kwargs = cloudpickle.loads(base64.b64decode(serialized_data["kwargs"]))
        else:
            args = json.loads(serialized_data["args"])
            kwargs = json.loads(serialized_data["kwargs"])
            
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
    try:
        # Use cloudpickle for better serialization
        serialized_result = base64.b64encode(cloudpickle.dumps(result)).decode('utf-8')
        
        return {
            "result": serialized_result,
            "serialization_method": "cloudpickle",
            "success": True
        }
    except Exception as e:
        log_debug(f"Cloudpickle result serialization failed: {e}, falling back to JSON")
        
        # Fallback to JSON
        try:
            return {
                "result": json.dumps(result),
                "serialization_method": "json", 
                "success": True
            }
        except Exception as json_e:
            # If all else fails, convert to string
            return {
                "result": str(result),
                "serialization_method": "string",
                "success": True
            }

def deserialize_result(serialized_data: Dict[str, Any]) -> Any:
    """
    Deserialize function result received from server.
    
    Args:
        serialized_data: Dict containing serialized result
        
    Returns:
        Deserialized result
    """
    if not serialized_data.get("success", True):
        error = serialized_data.get("error", "Unknown error")
        raise RuntimeError(f"Remote execution failed: {error}")
    
    method = serialized_data.get("serialization_method", "json")
    result_data = serialized_data["result"]
    
    try:
        if method == "cloudpickle":
            return cloudpickle.loads(base64.b64decode(result_data))
        elif method == "json":
            return json.loads(result_data)
        else:
            # String fallback
            return result_data
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