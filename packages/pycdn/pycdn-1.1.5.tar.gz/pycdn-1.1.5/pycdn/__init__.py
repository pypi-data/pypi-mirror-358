"""
PyCDN - The Netflix of Python packages 🚀

Revolutionary hybrid import system supporting both:
- Classic access: cdn.openai.OpenAI()  
- Natural imports: from cdn.openai import OpenAI

All through the same backend with lazy loading, caching, and smart enhancements.
"""

__version__ = "1.1.5"
__author__ = "PyCDN Team"
__description__ = "Revolutionary CDN-based Python package delivery with hybrid import system"

from .client import (
    # Core client functionality
    CDNClient, 
    pkg,
    
    # Lazy loading system
    LazyPackage,
    LazyModule,
    LazyFunction, 
    LazyClass,
    LazyInstance,
    
    # Hybrid import system - unified natural & classic syntax
    register_hybrid_cdn,
    unregister_hybrid_cdn,
    get_hybrid_mappings,
    clear_hybrid_mappings,
    install_hybrid_finder,
    uninstall_hybrid_finder,
    HybridCDNProxy,
    
    # Legacy compatibility (for backward compatibility)
    register_cdn_client,
    unregister_cdn_client, 
    get_cdn_mappings,
    clear_cdn_mappings
)

from .server import CDNServer, PackageDeployer

# Export everything for easy access
__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__description__",
    
    # Core client
    "CDNClient",
    "pkg",
    
    # Lazy loading system  
    "LazyPackage",
    "LazyModule",
    "LazyFunction",
    "LazyClass", 
    "LazyInstance",
    
    # Hybrid import system (main interface)
    "register_hybrid_cdn",
    "unregister_hybrid_cdn",
    "get_hybrid_mappings", 
    "clear_hybrid_mappings",
    "install_hybrid_finder",
    "uninstall_hybrid_finder", 
    "HybridCDNProxy",
    
    # Legacy compatibility 
    "register_cdn_client",
    "unregister_cdn_client",
    "get_cdn_mappings",
    "clear_cdn_mappings",
    
    # Server components
    "CDNServer",
    "PackageDeployer"
]

# Convenience shortcuts
connect = pkg  # Alternative name for pkg()

def info():
    """Display PyCDN information and capabilities."""
    return {
        "version": __version__,
        "description": __description__,
        "features": [
            "🎯 Classic access: cdn.openai.OpenAI()",
            "🌟 Natural imports: from cdn.openai import OpenAI", 
            "⚡ Lazy loading with intelligent caching",
            "📊 Built-in profiling and performance monitoring",
            "🔄 Package aliasing and reload capabilities",
            "🛠️ Development mode with local fallbacks",
            "🔍 Advanced introspection and debugging tools",
            "🌐 Multi-CDN support with custom prefixes"
        ],
        "hybrid_system": "Both syntax patterns use the same backend",
        "smart_enhancements": [
            "cdn.reload() - Force refresh packages",
            "cdn.profile() - Get performance metrics", 
            "cdn.alias() - Create package shortcuts",
            "cdn.dev_mode() - Enable local fallbacks",
            "cdn.list_packages() - Discover available packages",
            "cdn.describe() - Get detailed symbol information"
        ]
    }

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