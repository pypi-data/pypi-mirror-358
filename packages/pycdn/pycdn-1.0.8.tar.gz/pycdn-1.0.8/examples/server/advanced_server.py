#!/usr/bin/env python3
"""
PyCDN Server Example

This example demonstrates how to set up and run a PyCDN server for serving
Python packages via CDN with lazy loading.
"""

import asyncio
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pycdn.server import CDNServer, PackageDeployer
from pycdn.utils.common import set_debug_mode


def main():
    """Main server example."""
    print("=== PyCDN Server Example ===\n")
    
    # Enable debug mode for detailed logging
    set_debug_mode(True)
    
    # List of packages to make available via CDN
    allowed_packages = [
        "requests",
        "json",
        "math", 
        "random",
        "datetime",
        "os",
        "sys"
    ]
    
    print("Creating CDN server...")
    
    # Create CDN server instance
    server = CDNServer(
        host="localhost",
        port=8000,
        debug=True,
        allowed_packages=allowed_packages
    )
    
    print(f"CDN server configured for packages: {allowed_packages}")
    print(f"Server will run at: http://localhost:8000")
    print("\nAvailable endpoints:")
    print("  GET  /                     - Server info")
    print("  GET  /health               - Health check")
    print("  POST /execute              - Execute function")
    print("  GET  /packages             - List packages")
    print("  GET  /packages/{name}/info - Package info")
    print("  GET  /stats                - Server statistics")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        server.run()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")
        return 1
    
    return 0


def deploy_packages_example():
    """Example of deploying packages to a CDN server."""
    print("\n=== Package Deployment Example ===\n")
    
    # Create package deployer
    deployer = PackageDeployer("http://localhost:8000")
    
    # Packages to deploy
    packages_to_deploy = [
        "requests",
        "json", 
        "math",
        "random"
    ]
    
    print("Deploying packages...")
    
    for package_name in packages_to_deploy:
        try:
            print(f"Deploying {package_name}...")
            
            result = deployer.deploy_package(
                package_name=package_name,
                version="latest",
                dependencies=[],
                compute_requirements={"cpu": "1vcpu", "memory": "256MB"},
                edge_locations=["local"]
            )
            
            print(f"✓ {package_name} deployed successfully")
            print(f"  Status: {result['status']}")
            print(f"  Version: {result['version']}")
            
        except Exception as e:
            print(f"✗ Failed to deploy {package_name}: {e}")
    
    print(f"\nDeployed packages: {deployer.list_deployments()}")


async def async_server_example():
    """Example of running server asynchronously."""
    print("\n=== Async Server Example ===\n")
    
    server = CDNServer(
        host="localhost",
        port=8001,  # Different port for async example
        debug=True,
        allowed_packages=["requests", "json", "math"]
    )
    
    print("Starting async server on port 8001...")
    print("This allows running other code while server is running")
    
    # Start server asynchronously
    server_task = asyncio.create_task(server.start_async())
    
    # Do other work while server runs
    await asyncio.sleep(2)
    print("Server is running asynchronously...")
    
    # In a real application, you would do other work here
    await asyncio.sleep(3)
    
    print("Stopping async server...")
    server_task.cancel()
    
    try:
        await server_task
    except asyncio.CancelledError:
        print("Async server stopped")


def run_deployment_example():
    """Run the deployment example separately."""
    try:
        deploy_packages_example()
    except ConnectionError:
        print("Note: This requires a running CDN server at http://localhost:8000")
        print("Start the server first with: python examples/server_example.py")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PyCDN Server Examples")
    parser.add_argument(
        "--mode",
        choices=["server", "deploy", "async"],
        default="server",
        help="Example mode to run"
    )
    
    args = parser.parse_args()
    
    if args.mode == "server":
        sys.exit(main())
    elif args.mode == "deploy":
        run_deployment_example()
    elif args.mode == "async":
        asyncio.run(async_server_example()) 