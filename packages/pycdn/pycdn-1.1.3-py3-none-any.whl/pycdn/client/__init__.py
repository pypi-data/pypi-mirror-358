"""
PyCDN Client - Hybrid Import System

Provides both classic CDN access (cdn.package.Class) and natural imports 
(from cdn.package import Class) through a unified system.
"""

from .core import CDNClient, pkg
from .lazy_loader import LazyPackage, LazyModule, LazyFunction, LazyClass, LazyInstance
from .import_hook import (
    # Hybrid import system
    register_hybrid_cdn,
    unregister_hybrid_cdn,
    get_hybrid_mappings,
    clear_hybrid_mappings,
    install_hybrid_finder,
    uninstall_hybrid_finder,
    HybridCDNProxy,
    # Legacy aliases for backward compatibility
    register_hybrid_cdn as register_cdn_client,
    unregister_hybrid_cdn as unregister_cdn_client,
    get_hybrid_mappings as get_cdn_mappings,
    clear_hybrid_mappings as clear_cdn_mappings
)

__all__ = [
    # Core client
    'CDNClient',
    'pkg',
    
    # Lazy loading classes
    'LazyPackage',
    'LazyModule', 
    'LazyFunction',
    'LazyClass',
    'LazyInstance',
    
    # Hybrid import system
    'register_hybrid_cdn',
    'unregister_hybrid_cdn', 
    'get_hybrid_mappings',
    'clear_hybrid_mappings',
    'install_hybrid_finder',
    'uninstall_hybrid_finder',
    'HybridCDNProxy',
    
    # Legacy compatibility
    'register_cdn_client',
    'unregister_cdn_client',
    'get_cdn_mappings', 
    'clear_cdn_mappings'
]