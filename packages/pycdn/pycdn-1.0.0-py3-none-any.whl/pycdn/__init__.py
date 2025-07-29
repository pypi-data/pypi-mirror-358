"""
PyCDN - Revolutionary Python package delivery via CDN with serverless execution and lazy loading

PyCDN eliminates dependency hell by delivering Python packages through a global CDN network 
with intelligent lazy loading. No more `pip install` - just import and use packages instantly 
from our edge-optimized servers.

Author: Harshal More <harshalmore2468@gmail.com>
License: Apache-2.0
Version: 0.1.0
"""

__version__ = "1.0.0"
__author__ = "Harshal More"
__email__ = "harshalmore2468@gmail.com"
__license__ = "Apache-2.0"

# Core client functionality
from .client.core import CDNClient, pkg, connect, configure, preload

# Server functionality 
from .server.core import CDNServer, PackageDeployer

# Utility functions
from .utils.common import get_version, set_debug_mode

# Make primary functions available at package level
__all__ = [
    # Client API
    "pkg",
    "connect", 
    "configure",
    "preload",
    "CDNClient",
    
    # Server API
    "CDNServer",
    "PackageDeployer",
    
    # Utilities
    "get_version",
    "set_debug_mode",
    
    # Metadata
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
]

# Initialize global configuration
_global_config = {
    "debug": False,
    "default_timeout": 30,
    "cache_size": "100MB",
    "max_retries": 3,
}

def get_config():
    """Get global PyCDN configuration."""
    return _global_config.copy()

def set_config(**kwargs):
    """Set global PyCDN configuration."""
    _global_config.update(kwargs) 