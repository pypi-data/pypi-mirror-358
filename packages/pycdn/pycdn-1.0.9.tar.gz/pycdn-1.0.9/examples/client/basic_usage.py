"""
PyCDN Basic Usage Example

This example demonstrates the core functionality of PyCDN - 
using Python packages remotely without local installation.

Usage:
    # First start a server:
    python examples/server/basic_server.py
    
    # Then run this client:
    python examples/client/basic_usage.py

Perfect for getting started with PyCDN!
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pycdn


def main():
    """Basic PyCDN usage examples"""
    print("🚀 PyCDN Basic Usage Example")
    print("="*40)
    
    # Method 1: Quick access to CDN packages
    print("\n📦 Method 1: Quick Package Access")
    print("-" * 30)
    
    try:
        # Connect to local CDN server
        cdn_packages = pycdn.pkg("http://localhost:8000")
        
        # Use math package functions remotely
        print("🧮 Math operations via CDN:")
        result1 = cdn_packages.math.sqrt(16)
        print(f"  sqrt(16) = {result1}")
        
        result2 = cdn_packages.math.factorial(5)
        print(f"  factorial(5) = {result2}")
        
        # Use json package
        print("\n📄 JSON operations via CDN:")
        data = {"name": "PyCDN", "version": "1.0.0", "awesome": True}
        json_str = cdn_packages.json.dumps(data)
        print(f"  dumps() = {json_str}")
        
        parsed = cdn_packages.json.loads(json_str)
        print(f"  loads() = {parsed}")
        
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    # Method 2: Full client with configuration
    print("\n📡 Method 2: Full Client Configuration")
    print("-" * 35)
    
    try:
        # Create client with custom settings
        client = pycdn.connect(
            url="http://localhost:8000",
            timeout=30,
            cache_size="50MB",
            max_retries=3
        )
        
        # List available packages
        packages = client.list_packages()
        print(f"📦 Available packages: {packages}")
        
        # Get package information
        if "math" in packages:
            info = client.get_package_info("math")
            print(f"📋 Math package info: {info}")
        
        # Call functions directly
        print("\n🔢 Direct function calls:")
        result = client.call_function("math", "pow", (2, 8))
        print(f"  math.pow(2, 8) = {result}")
        
        result = client.call_function("os", "getcwd")
        print(f"  os.getcwd() = {result}")
        
        # Get client statistics
        stats = client.get_stats()
        print(f"\n📊 Client stats: {stats}")
        
        # Close client
        client.close()
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    # Method 3: Using import hooks (advanced)
    print("\n🔗 Method 3: Import Hook Integration")
    print("-" * 32)
    
    try:
        # Install import hook for automatic CDN package loading
        pycdn.install_import_hook("http://localhost:8000", ["cdn_", "pycdn_", "remote_"])
        
        # Now you can import packages as if they were local!
        # Note: This is advanced usage and requires the import hook
        print("✨ Import hook installed!")
        print("   You can now use 'from cdn_math import sqrt' syntax")
        print("   Prefixes: cdn_, pycdn_, remote_")
        
        # Uninstall hook
        pycdn.uninstall_import_hook()
        print("🔄 Import hook uninstalled")
        
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    print("\n✅ Basic usage examples completed!")
    print("\n💡 Next steps:")
    print("   • Try the streaming demo: python examples/streaming_demo.py")
    print("   • Check server examples: python examples/server_example.py")
    print("   • Explore OpenAI integration: python examples/openai_example.py")


if __name__ == "__main__":
    # Check if server is running
    try:
        client = pycdn.connect("http://localhost:8000", timeout=5)
        client.close()
        print("✅ PyCDN server detected at http://localhost:8000")
    except:
        print("⚠️  PyCDN server not running!")
        print("Please start it first with: pycdn server start")
        print("Then run this example again.\n")
    
    main() 