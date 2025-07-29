"""
PyCDN Client Example

This example demonstrates how to use the PyCDN client to consume packages
from a CDN server with lazy loading.

Usage:
    # First start a server:
    python examples/server/basic_server.py
    
    # Then run this client:
    python examples/client/client_example.py
"""

import sys
import os
import time

# Add parent directory to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pycdn
from pycdn.utils.common import set_debug_mode


def basic_client_usage():
    """Demonstrate basic PyCDN client usage."""
    print("=== Basic PyCDN Client Usage ===\n")
    
    # Enable debug mode to see what's happening
    set_debug_mode(True)
    
    # Connect to CDN server
    print("Connecting to CDN server...")
    cdn_url = "http://localhost:8000"
    
    try:
        # Method 1: Using pkg() function (recommended)
        print(f"Creating lazy package namespace from {cdn_url}")
        pycdn_packages = pycdn.pkg(url=cdn_url)
        
        print("✓ Connected to CDN server")
        
        # Access packages lazily
        print("\n--- Accessing Python standard library packages ---")
        
        # Math package
        print("Loading math package...")
        math_pkg = pycdn_packages.math
        
        # Call math functions remotely
        print("Calling math.sqrt(16)...")
        result = math_pkg.sqrt(16)
        print(f"Result: {result}")
        
        print("Calling math.pi...")
        pi_value = math_pkg.pi
        print(f"Pi value: {pi_value}")
        
        # Random package
        print("\nLoading random package...")
        random_pkg = pycdn_packages.random
        
        print("Calling random.randint(1, 100)...")
        random_num = random_pkg.randint(1, 100)
        print(f"Random number: {random_num}")
        
        # JSON package
        print("\nLoading json package...")
        json_pkg = pycdn_packages.json
        
        data = {"message": "Hello from CDN!", "numbers": [1, 2, 3]}
        print(f"Data to serialize: {data}")
        
        json_str = json_pkg.dumps(data)
        print(f"JSON string: {json_str}")
        
        parsed_data = json_pkg.loads(json_str)
        print(f"Parsed back: {parsed_data}")
        
    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("Make sure the CDN server is running:")
        print("  python examples/server_example.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def advanced_client_usage():
    """Demonstrate advanced PyCDN client features."""
    print("\n=== Advanced PyCDN Client Usage ===\n")
    
    # Method 2: Using connect() for more control
    print("Creating CDN client with custom configuration...")
    
    try:
        client = pycdn.connect(
            url="http://localhost:8000",
            timeout=30,
            cache_size="50MB",
            max_retries=5
        )
        
        print("✓ CDN client created")
        
        # Get server information
        print("\n--- Server Information ---")
        packages = client.list_packages()
        print(f"Available packages: {packages}")
        
        # Get package information
        if packages:
            package_name = packages[0]
            print(f"\nGetting info for package: {package_name}")
            info = client.get_package_info(package_name)
            print(f"Package info: {info}")
        
        # Get server statistics
        print("\n--- Server Statistics ---")
        stats = client.get_stats()
        print(f"Server stats: {stats}")
        
        # Preload packages for better performance
        print("\n--- Preloading Packages ---")
        client.preload_packages(["math", "random", "json"])
        print("✓ Packages preloaded")
        
        # Create lazy package namespace
        print("\n--- Using Lazy Packages ---")
        from pycdn.client.lazy_loader import LazyPackage
        lazy_packages = LazyPackage(client)
        
        # Use preloaded packages (should be faster)
        print("Using preloaded math package...")
        start_time = time.time()
        result = lazy_packages.math.pow(2, 8)
        end_time = time.time()
        print(f"math.pow(2, 8) = {result} (took {end_time - start_time:.3f}s)")
        
        # Clear cache and try again
        print("\nClearing cache and trying again...")
        client.clear_cache()
        
        start_time = time.time()
        result = lazy_packages.math.pow(3, 4)
        end_time = time.time()
        print(f"math.pow(3, 4) = {result} (took {end_time - start_time:.3f}s)")
        
        # Close client when done
        client.close()
        print("✓ Client closed")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def configuration_example():
    """Demonstrate PyCDN configuration options."""
    print("\n=== Configuration Example ===\n")
    
    # Global configuration
    print("Setting global configuration...")
    pycdn.configure(
        default_url="http://localhost:8000",
        timeout=60,
        cache_size="200MB",
        max_retries=3
    )
    print("✓ Global configuration set")
    
    # Preload common packages globally
    print("\nPreloading packages globally...")
    try:
        pycdn.preload(["math", "json", "random"])
        print("✓ Packages preloaded globally")
    except Exception as e:
        print(f"✗ Preload failed: {e}")
    
    # Use with different CDN endpoints
    print("\n--- Multiple CDN Endpoints ---")
    
    # You could connect to different CDN servers
    endpoints = [
        "http://localhost:8000",  # Local development
        # "https://cdn.python.dev",     # Public CDN (example)
        # "https://enterprise.pycdn.com"  # Enterprise CDN (example)
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing endpoint: {endpoint}")
            test_client = pycdn.connect(endpoint, timeout=5)
            packages = test_client.list_packages()
            print(f"  ✓ Available packages: {len(packages)}")
            test_client.close()
        except Exception as e:
            print(f"  ✗ Failed: {e}")


def performance_comparison():
    """Compare performance of local vs CDN package usage."""
    print("\n=== Performance Comparison ===\n")
    
    try:
        # Test CDN performance
        print("Testing CDN package performance...")
        cdn_packages = pycdn.pkg("http://localhost:8000")
        
        # Time multiple operations
        operations = [
            ("math.sqrt(100)", lambda: cdn_packages.math.sqrt(100)),
            ("math.factorial(10)", lambda: cdn_packages.math.factorial(10)),
            ("random.randint(1, 1000)", lambda: cdn_packages.random.randint(1, 1000)),
            ("json.dumps({'test': 123})", lambda: cdn_packages.json.dumps({"test": 123})),
        ]
        
        print("\nCDN Performance:")
        for desc, operation in operations:
            start_time = time.time()
            result = operation()
            end_time = time.time()
            print(f"  {desc}: {result} ({end_time - start_time:.3f}s)")
        
        # Compare with local imports (if available)
        print("\nLocal Performance (for comparison):")
        import math, random, json
        
        local_operations = [
            ("math.sqrt(100)", lambda: math.sqrt(100)),
            ("math.factorial(10)", lambda: math.factorial(10)),
            ("random.randint(1, 1000)", lambda: random.randint(1, 1000)),
            ("json.dumps({'test': 123})", lambda: json.dumps({"test": 123})),
        ]
        
        for desc, operation in local_operations:
            start_time = time.time()
            result = operation()
            end_time = time.time()
            print(f"  {desc}: {result} ({end_time - start_time:.3f}s)")
        
        print("\nNote: CDN calls include network overhead but eliminate local dependencies!")
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")


def error_handling_example():
    """Demonstrate error handling with PyCDN."""
    print("\n=== Error Handling Example ===\n")
    
    try:
        # Connect to CDN
        cdn_packages = pycdn.pkg("http://localhost:8000")
        
        print("Testing various error scenarios...")
        
        # Test 1: Non-existent package
        print("\n1. Testing non-existent package...")
        try:
            result = cdn_packages.nonexistent_package.some_function()
            print(f"Unexpected success: {result}")
        except Exception as e:
            print(f"  ✓ Expected error: {e}")
        
        # Test 2: Non-existent function
        print("\n2. Testing non-existent function...")
        try:
            result = cdn_packages.math.nonexistent_function(42)
            print(f"Unexpected success: {result}")
        except Exception as e:
            print(f"  ✓ Expected error: {e}")
        
        # Test 3: Invalid arguments
        print("\n3. Testing invalid arguments...")
        try:
            result = cdn_packages.math.sqrt("not a number")
            print(f"Unexpected success: {result}")
        except Exception as e:
            print(f"  ✓ Expected error: {e}")
        
        print("\n✓ Error handling working correctly")
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")


def main():
    """Run all client examples."""
    print("PyCDN Client Examples")
    print("=" * 50)
    
    # Check if server is running
    try:
        client = pycdn.connect("http://localhost:8000", timeout=5)
        client.list_packages()
        client.close()
        print("✓ CDN server is running\n")
    except Exception as e:
        print("✗ CDN server not available")
        print("Please start the server first:")
        print("  python examples/server_example.py")
        print(f"Error: {e}\n")
        return 1
    
    # Run examples
    success = True
    
    success &= basic_client_usage()
    success &= advanced_client_usage() 
    configuration_example()
    performance_comparison()
    error_handling_example()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All examples completed successfully!")
    else:
        print("✗ Some examples failed")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 