#!/usr/bin/env python3
"""
PyCDN OpenAI Integration Example

This example demonstrates how to use the OpenAI package via PyCDN,
showcasing real-world usage of external packages through CDN delivery.

Usage:
    # First start a server:
    python examples/server/basic_server.py
    
    # Set API key (optional for mock demo):
    export OPENAI_API_KEY="your-key-here"
    
    # Then run this client:
    python examples/client/openai_example.py

Note: This example requires the OpenAI package to be installed on the server
and a valid OpenAI API key for actual API calls.
"""

import sys
import os
import time

# Add parent directory to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pycdn
from pycdn.utils.common import set_debug_mode


def setup_openai_server():
    """Setup and start a CDN server with OpenAI package support."""
    print("=== Setting up OpenAI CDN Server ===\n")
    
    try:
        from pycdn.server import CDNServer
        
        # Create server with OpenAI package allowed
        server = CDNServer(
            host="localhost",
            port=8000,
            debug=True,
            allowed_packages=["openai", "json", "os", "sys", "time"]
        )
        
        print("OpenAI CDN server configured")
        print("Allowed packages: openai, json, os, sys, time")
        print("Server will run at: http://localhost:8000")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start server
        server.run()
        
    except ImportError:
        print("OpenAI package not available on server")
        print("Install with: pip install openai")
        return False
    except KeyboardInterrupt:
        print("\nServer stopped")
        return True
    except Exception as e:
        print(f"Server error: {e}")
        return False


def openai_client_example():
    """Demonstrate using OpenAI package via PyCDN."""
    print("=== OpenAI PyCDN Client Example ===\n")
    
    # Enable debug mode
    set_debug_mode(True)
    
    try:
        # Connect to CDN server
        print("Connecting to CDN server...")
        cdn_packages = pycdn.pkg("http://localhost:8000")
        
        print("✓ Connected to CDN server")
        
        # Access OpenAI package lazily
        print("\nLoading OpenAI package from CDN...")
        openai_pkg = cdn_packages.openai
        
        print("✓ OpenAI package loaded lazily")
        
        # Example 1: Basic OpenAI client setup (without actual API call)
        print("\n--- OpenAI Client Setup Example ---")
        
        # Note: In a real scenario, you would set your API key
        # For this example, we'll demonstrate the package loading
        
        try:
            # This would normally create an OpenAI client
            # client = openai_pkg.OpenAI(api_key="your-api-key-here")
            print("OpenAI client class available via CDN")
            
            # Demonstrate accessing OpenAI module attributes
            print("Checking OpenAI package version...")
            # version = openai_pkg.__version__
            # print(f"OpenAI version: {version}")
            
        except Exception as e:
            print(f"Note: {e}")
            print("This is expected if OpenAI package is not installed on server")
        
        # Example 2: Mock OpenAI usage simulation
        print("\n--- Simulated OpenAI Usage ---")
        
        # Simulate typical OpenAI workflow using standard library packages
        json_pkg = cdn_packages.json
        
        # Create a mock request payload
        mock_request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello from PyCDN!"}
            ],
            "max_tokens": 100
        }
        
        print("Mock OpenAI request payload:")
        request_json = json_pkg.dumps(mock_request, indent=2)
        print(request_json)
        
        # Mock response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Hello! I'm responding via PyCDN lazy loading. This demonstrates how external packages can be served through CDN!"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 25,
                "total_tokens": 35
            }
        }
        
        print("\nMock OpenAI response:")
        response_json = json_pkg.dumps(mock_response, indent=2)
        print(response_json)
        
        # Parse response
        parsed_response = json_pkg.loads(response_json)
        message_content = parsed_response["choices"][0]["message"]["content"]
        print(f"\nExtracted message: {message_content}")
        
        print("\n✓ OpenAI package integration successful!")
        
    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("Make sure the CDN server is running with OpenAI support:")
        print("  python examples/openai_example.py --mode server")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True


def real_openai_example():
    """
    Example of real OpenAI API usage via PyCDN (requires API key).
    
    This demonstrates how you would actually use OpenAI through PyCDN
    in a production environment.
    """
    print("=== Real OpenAI API Example ===\n")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No OpenAI API key found in environment")
        print("Set OPENAI_API_KEY environment variable to run this example")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Connect to CDN
        print("Connecting to CDN for real OpenAI usage...")
        cdn_packages = pycdn.pkg("http://localhost:8000")
        
        # Load OpenAI package
        openai_pkg = cdn_packages.openai
        
        print("Creating OpenAI client via CDN...")
        
        # Create OpenAI client
        client = openai_pkg.OpenAI(api_key=api_key)
        
        print("Making API call via CDN...")
        
        # Make a simple API call
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user", 
                    "content": "Explain what PyCDN is in one sentence."
                }
            ],
            max_tokens=50
        )
        
        # Extract response
        response_content = completion.choices[0].message.content
        
        print("\n--- OpenAI Response via PyCDN ---")
        print(f"Response: {response_content}")
        print(f"Tokens used: {completion.usage.total_tokens}")
        
        print("\n✓ Real OpenAI API call successful via PyCDN!")
        
        return True
        
    except Exception as e:
        print(f"✗ Real OpenAI example failed: {e}")
        return False


def performance_benchmark():
    """Benchmark OpenAI package loading via PyCDN vs local."""
    print("\n=== Performance Benchmark ===\n")
    
    try:
        # Benchmark CDN loading
        print("Benchmarking CDN package loading...")
        
        start_time = time.time()
        cdn_packages = pycdn.pkg("http://localhost:8000")
        openai_pkg = cdn_packages.openai
        # Trigger actual loading by accessing an attribute
        _ = str(openai_pkg)
        cdn_time = time.time() - start_time
        
        print(f"CDN loading time: {cdn_time:.3f}s")
        
        # Benchmark local import (if available)
        try:
            print("\nBenchmarking local import...")
            start_time = time.time()
            import openai
            local_time = time.time() - start_time
            print(f"Local import time: {local_time:.3f}s")
            
            # Compare
            print(f"\nComparison:")
            print(f"  CDN: {cdn_time:.3f}s")
            print(f"  Local: {local_time:.3f}s")
            print(f"  Overhead: {(cdn_time - local_time):.3f}s")
            
        except ImportError:
            print("Local OpenAI package not available for comparison")
        
        # Multiple calls benchmark
        print("\n--- Multiple Function Calls Benchmark ---")
        
        json_pkg = cdn_packages.json
        
        # Warm up
        _ = json_pkg.dumps({"test": "warmup"})
        
        # Benchmark multiple calls
        start_time = time.time()
        for i in range(10):
            _ = json_pkg.dumps({"iteration": i, "data": list(range(10))})
        multi_call_time = time.time() - start_time
        
        print(f"10 JSON serialization calls via CDN: {multi_call_time:.3f}s")
        print(f"Average per call: {multi_call_time/10:.3f}s")
        
    except Exception as e:
        print(f"✗ Benchmark failed: {e}")


def deployment_example():
    """Example of deploying OpenAI package to CDN."""
    print("\n=== OpenAI Package Deployment ===\n")
    
    try:
        from pycdn.server import PackageDeployer
        
        # Create deployer
        deployer = PackageDeployer("http://localhost:8000")
        
        print("Deploying OpenAI package to CDN...")
        
        # Deploy OpenAI package
        result = deployer.deploy_package(
            package_name="openai",
            version="latest",
            dependencies=["httpx", "pydantic", "typing-extensions"],
            compute_requirements={
                "cpu": "2vcpu",
                "memory": "1GB"
            },
            edge_locations=["us-east", "eu-west", "asia-pacific"]
        )
        
        print("✓ OpenAI package deployed successfully")
        print(f"Status: {result['status']}")
        print(f"Version: {result['version']}")
        print(f"Dependencies: {result['dependencies']}")
        print(f"Edge locations: {result['edge_locations']}")
        
        # List all deployments
        deployments = deployer.list_deployments()
        print(f"\nAll deployed packages: {deployments}")
        
    except Exception as e:
        print(f"✗ Deployment failed: {e}")


def main():
    """Main function to run OpenAI examples."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PyCDN OpenAI Integration Examples")
    parser.add_argument(
        "--mode",
        choices=["server", "client", "real", "benchmark", "deploy"],
        default="client",
        help="Example mode to run"
    )
    
    args = parser.parse_args()
    
    print("PyCDN OpenAI Integration Examples")
    print("=" * 50)
    
    if args.mode == "server":
        # Start server with OpenAI support
        return 0 if setup_openai_server() else 1
    
    elif args.mode == "client":
        # Run client examples
        success = openai_client_example()
        return 0 if success else 1
    
    elif args.mode == "real":
        # Run real OpenAI API example
        success = real_openai_example()
        return 0 if success else 1
    
    elif args.mode == "benchmark":
        # Run performance benchmark
        performance_benchmark()
        return 0
    
    elif args.mode == "deploy":
        # Run deployment example
        deployment_example()
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 