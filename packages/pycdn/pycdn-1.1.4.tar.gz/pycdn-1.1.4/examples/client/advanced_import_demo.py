#!/usr/bin/env python3
"""
Advanced Import Demo - PyCDN Meta Path Import System

This demo showcases the revolutionary import system that allows natural Python import syntax
like 'from cdn.openai import OpenAI' alongside the classic pycdn.pkg() approach.

Features demonstrated:
- Meta path import hook system
- Natural import syntax
- Class instantiation and method calls
- Error handling with PyCDNRemoteError
- Hybrid usage patterns
- Import prefix management
"""

import sys
import pycdn
from pycdn import PyCDNRemoteError


def demo_classic_usage():
    """Demonstrate the classic PyCDN usage pattern."""
    print("=" * 60)
    print("1. CLASSIC PYCDN USAGE")
    print("=" * 60)
    
    # Connect to CDN server with default prefix 'cdn'
    cdn = pycdn.pkg("http://localhost:8000")
    
    print(f"Created CDN connection: {cdn}")
    print(f"Available via import prefix: {cdn._prefix}")
    
    try:
        # Classic attribute access
        result = cdn.math.sqrt(16)
        print(f"cdn.math.sqrt(16) = {result}")
        
        # Function composition
        result = cdn.math.pow(2, 3)
        print(f"cdn.math.pow(2, 3) = {result}")
        
    except Exception as e:
        print(f"Error in classic usage: {e}")


def demo_natural_imports():
    """Demonstrate the new natural import syntax."""
    print("\n" + "=" * 60)
    print("2. NATURAL IMPORT SYNTAX")
    print("=" * 60)
    
    try:
        # This works because pycdn.pkg() registered the 'cdn' prefix
        from cdn.math import sqrt, pow
        print("Successfully imported: from cdn.math import sqrt, pow")
        
        # Use functions naturally
        result1 = sqrt(25)
        result2 = pow(3, 4)
        print(f"sqrt(25) = {result1}")
        print(f"pow(3, 4) = {result2}")
        
        # Import classes
        from cdn.openai import OpenAI
        print("Successfully imported: from cdn.openai import OpenAI")
        
        # Create instance (this would work with real OpenAI package)
        # client = OpenAI(api_key="test-key")
        # print(f"Created OpenAI client: {client}")
        
    except PyCDNRemoteError as e:
        print(f"CDN Remote Error: {e}")
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Note: This is expected if the CDN server doesn't have these packages")


def demo_custom_prefix():
    """Demonstrate custom import prefixes."""
    print("\n" + "=" * 60)
    print("3. CUSTOM IMPORT PREFIX")
    print("=" * 60)
    
    # Create CDN connection with custom prefix
    remote = pycdn.pkg("http://localhost:8000", prefix="remote")
    print(f"Created remote CDN with prefix: {remote._prefix}")
    
    try:
        # Now we can import from 'remote' prefix
        from remote.numpy import array, mean
        print("Successfully imported: from remote.numpy import array, mean")
        
        # Use the functions
        data = array([1, 2, 3, 4, 5])
        avg = mean(data)
        print(f"array([1,2,3,4,5]) = {data}")
        print(f"mean(data) = {avg}")
        
    except Exception as e:
        print(f"Error with custom prefix: {e}")


def demo_multiple_cdns():
    """Demonstrate multiple CDN connections with different prefixes."""
    print("\n" + "=" * 60)
    print("4. MULTIPLE CDN CONNECTIONS")
    print("=" * 60)
    
    # Connect to multiple CDN servers
    prod_cdn = pycdn.pkg("http://prod-cdn:8000", prefix="prod")
    dev_cdn = pycdn.pkg("http://dev-cdn:8000", prefix="dev")
    
    print("Connected to multiple CDNs:")
    print(f"  Production: {prod_cdn}")
    print(f"  Development: {dev_cdn}")
    
    # Show current mappings
    mappings = pycdn.get_cdn_mappings()
    print("\nActive CDN mappings:")
    for prefix, url in mappings.items():
        print(f"  {prefix} -> {url}")
    
    try:
        # Import from different CDNs
        from prod.stable_package import stable_function
        from dev.beta_package import beta_function
        
        print("Successfully imported from different CDNs")
        
    except Exception as e:
        print(f"Multiple CDN demo error: {e}")


def demo_dynamic_prefix_management():
    """Demonstrate dynamic prefix management."""
    print("\n" + "=" * 60)
    print("5. DYNAMIC PREFIX MANAGEMENT")
    print("=" * 60)
    
    cdn = pycdn.pkg("http://localhost:8000", prefix="initial")
    print(f"Initial prefix: {cdn._prefix}")
    
    # Change prefix dynamically
    cdn.set_prefix("dynamic")
    print(f"Changed prefix to: {cdn._prefix}")
    
    # Enable specific package imports
    cdn.enable_imports(["tensorflow", "pytorch", "scikit-learn"])
    print("Enabled direct imports for ML packages")
    
    try:
        # These would now work:
        # from dynamic.tensorflow import keras
        # from dynamic.pytorch import nn
        # from dynamic.scikit-learn import ensemble
        
        print("Package-specific imports enabled (would work with real packages)")
        
    except Exception as e:
        print(f"Dynamic management demo error: {e}")


def demo_error_handling():
    """Demonstrate comprehensive error handling."""
    print("\n" + "=" * 60)
    print("6. ERROR HANDLING")
    print("=" * 60)
    
    cdn = pycdn.pkg("http://localhost:8000")
    
    try:
        # Try to import non-existent package
        from cdn.nonexistent_package import some_function
        result = some_function()
        
    except PyCDNRemoteError as e:
        print(f"Caught PyCDNRemoteError: {e.message}")
        if e.package_name:
            print(f"Package: {e.package_name}")
        if e.remote_traceback:
            print("Remote traceback available")
            
    except ImportError as e:
        print(f"Caught ImportError: {e}")
        
    except Exception as e:
        print(f"Caught general exception: {e}")


def demo_hybrid_usage():
    """Demonstrate hybrid usage patterns."""
    print("\n" + "=" * 60)
    print("7. HYBRID USAGE PATTERNS")
    print("=" * 60)
    
    # Classic usage
    cdn = pycdn.pkg("http://localhost:8000")
    
    try:
        # Mix classic and import syntax
        classic_result = cdn.math.factorial(5)
        print(f"Classic: cdn.math.factorial(5) = {classic_result}")
        
        # Then use imports for the same package
        from cdn.math import factorial
        import_result = factorial(5)
        print(f"Import: factorial(5) = {import_result}")
        
        print("Both methods work seamlessly together!")
        
    except Exception as e:
        print(f"Hybrid usage error: {e}")


def demo_development_mode():
    """Demonstrate development mode features."""
    print("\n" + "=" * 60)
    print("8. DEVELOPMENT MODE")
    print("=" * 60)
    
    # Configure for development
    pycdn.configure(debug=True, timeout=60)
    
    cdn = pycdn.pkg("http://localhost:8000", prefix="dev")
    
    # In real implementation, this would enable:
    # - Local fallback for offline development
    # - Enhanced debugging
    # - Development server auto-discovery
    # - Mock mode for testing
    
    print("Development mode configured:")
    print("  - Debug logging enabled")
    print("  - Extended timeouts")
    print("  - Local fallback available (in full implementation)")
    print("  - Mock mode support (in full implementation)")


def cleanup_demo():
    """Clean up demo state."""
    print("\n" + "=" * 60)
    print("9. CLEANUP")
    print("=" * 60)
    
    # Show current state
    mappings = pycdn.get_cdn_mappings()
    print(f"Current CDN mappings: {len(mappings)}")
    
    # Clear all mappings
    pycdn.clear_cdn_mappings()
    
    # Verify cleanup
    mappings = pycdn.get_cdn_mappings()
    print(f"After cleanup: {len(mappings)} mappings")
    
    print("Demo cleanup complete!")


if __name__ == "__main__":
    print("PyCDN Advanced Import Demo")
    print("Showcasing the revolutionary meta path import system")
    print("Note: This demo requires a running PyCDN server at http://localhost:8000")
    print("")
    
    try:
        demo_classic_usage()
        demo_natural_imports()
        demo_custom_prefix()
        demo_multiple_cdns()
        demo_dynamic_prefix_management()
        demo_error_handling()
        demo_hybrid_usage()
        demo_development_mode()
        cleanup_demo()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("The new PyCDN import system enables:")
        print("  ✓ Natural Python import syntax")
        print("  ✓ Seamless CDN package access")
        print("  ✓ Multiple CDN support")
        print("  ✓ Dynamic prefix management")
        print("  ✓ Comprehensive error handling")
        print("  ✓ Hybrid usage patterns")
        print("  ✓ Development mode features")
        print("\nPyCDN: The Netflix of Python packages! 🚀")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc() 