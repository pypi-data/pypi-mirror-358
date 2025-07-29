"""
Client-side SDK for PyCDN package consumption with lazy loading.
"""

from .core import CDNClient, pkg, connect, configure, preload
from .lazy_loader import LazyModule, LazyPackage
from .import_hook import install_import_hook, uninstall_import_hook

__all__ = [
    "CDNClient", 
    "pkg", 
    "connect", 
    "configure", 
    "preload",
    "LazyModule",
    "LazyPackage", 
    "install_import_hook",
    "uninstall_import_hook"
]