"""
Import hook system for transparent CDN package imports.

This is a simplified implementation for MVP. In production, this would integrate
more deeply with Python's import machinery.
"""

import sys
import importlib.util
from typing import Any, Dict, Optional
from ..utils.common import log_debug

# Global state for import hooks
_hook_installed = False
_original_import = None
_cdn_mappings = {}


def install_import_hook(cdn_url: str, package_prefixes: list) -> None:
    """
    Install import hook for CDN packages.
    
    Args:
        cdn_url: CDN server URL
        package_prefixes: List of package prefixes to intercept
    """
    global _hook_installed, _original_import, _cdn_mappings
    
    if _hook_installed:
        log_debug("Import hook already installed")
        return
    
    # Store CDN mappings
    for prefix in package_prefixes:
        _cdn_mappings[prefix] = cdn_url
    
    # Store original import function
    _original_import = __builtins__.__import__
    
    # Replace with our custom import
    __builtins__.__import__ = _custom_import
    
    _hook_installed = True
    log_debug(f"Import hook installed for prefixes: {package_prefixes}")


def uninstall_import_hook() -> None:
    """Uninstall import hook and restore original import."""
    global _hook_installed, _original_import, _cdn_mappings
    
    if not _hook_installed:
        log_debug("Import hook not installed")
        return
    
    # Restore original import
    if _original_import:
        __builtins__.__import__ = _original_import
    
    # Clear state
    _hook_installed = False
    _cdn_mappings.clear()
    _original_import = None
    
    log_debug("Import hook uninstalled")


def _custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Custom import function that intercepts CDN package imports.
    
    Args:
        name: Module name
        globals: Global namespace
        locals: Local namespace  
        fromlist: From list for relative imports
        level: Relative import level
        
    Returns:
        Module object
    """
    # Check if this is a CDN package
    for prefix, cdn_url in _cdn_mappings.items():
        if name.startswith(prefix):
            log_debug(f"Intercepting import of CDN package: {name}")
            
            # Create lazy module using CDN client
            from .core import CDNClient
            from .lazy_loader import LazyModule
            
            client = CDNClient(cdn_url)
            module = LazyModule(client, name)
            
            # Add to sys.modules
            sys.modules[name] = module
            
            return module
    
    # Use original import for non-CDN packages
    return _original_import(name, globals, locals, fromlist, level)


def add_cdn_mapping(prefix: str, cdn_url: str) -> None:
    """
    Add a CDN mapping for package prefix.
    
    Args:
        prefix: Package prefix to intercept
        cdn_url: CDN server URL
    """
    global _cdn_mappings
    _cdn_mappings[prefix] = cdn_url
    log_debug(f"Added CDN mapping: {prefix} -> {cdn_url}")


def remove_cdn_mapping(prefix: str) -> None:
    """
    Remove a CDN mapping.
    
    Args:
        prefix: Package prefix to remove
    """
    global _cdn_mappings
    if prefix in _cdn_mappings:
        del _cdn_mappings[prefix]
        log_debug(f"Removed CDN mapping: {prefix}")


def get_cdn_mappings() -> Dict[str, str]:
    """
    Get current CDN mappings.
    
    Returns:
        Dictionary of prefix -> CDN URL mappings
    """
    return _cdn_mappings.copy()


def is_hook_installed() -> bool:
    """
    Check if import hook is installed.
    
    Returns:
        True if hook is installed
    """
    return _hook_installed


# Convenience functions for common use cases
def enable_cdn_imports(cdn_url: str = "http://localhost:8000") -> None:
    """
    Enable CDN imports for common package prefixes.
    
    Args:
        cdn_url: CDN server URL
    """
    common_prefixes = ["pycdn_", "cdn_", "remote_"]
    install_import_hook(cdn_url, common_prefixes)


def disable_cdn_imports() -> None:
    """Disable CDN imports."""
    uninstall_import_hook() 