"""
Command-line interface for PyCDN.
"""

import argparse
import sys
import json
from typing import Any, Dict, List, Optional

from .server.core import CDNServer, PackageDeployer
from .client.core import CDNClient, connect
from .utils.common import set_debug_mode, get_version


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="pycdn",
        description="PyCDN - Revolutionary Python package delivery via CDN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pycdn server start                    # Start CDN server
  pycdn server start --port 8080       # Start server on port 8080
  pycdn client list                     # List packages on server
  pycdn client info requests            # Get info about requests package
  pycdn deploy requests                 # Deploy requests package
  pycdn stats                          # Show server statistics
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"PyCDN {get_version()}"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="CDN server URL (default: http://localhost:8000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Server commands
    server_parser = subparsers.add_parser("server", help="Server management")
    server_subparsers = server_parser.add_subparsers(dest="server_command")
    
    # Server start
    start_parser = server_subparsers.add_parser("start", help="Start CDN server")
    start_parser.add_argument("--host", default="localhost", help="Server host")
    start_parser.add_argument("--port", type=int, default=8000, help="Server port")
    start_parser.add_argument("--allowed-packages", nargs="*", help="Allowed packages")
    
    # Client commands
    client_parser = subparsers.add_parser("client", help="Client operations")
    client_subparsers = client_parser.add_subparsers(dest="client_command")
    
    # Client list
    client_subparsers.add_parser("list", help="List available packages")
    
    # Client info
    info_parser = client_subparsers.add_parser("info", help="Get package info")
    info_parser.add_argument("package", help="Package name")
    
    # Client stats
    client_subparsers.add_parser("stats", help="Get server statistics")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy package to CDN")
    deploy_parser.add_argument("package", help="Package name to deploy")
    deploy_parser.add_argument("--version", help="Package version")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test CDN connection")
    
    return parser


def handle_server_start(args: argparse.Namespace) -> int:
    """Handle server start command."""
    try:
        print(f"Starting PyCDN server on {args.host}:{args.port}")
        
        server = CDNServer(
            host=args.host,
            port=args.port,
            debug=args.debug,
            allowed_packages=args.allowed_packages
        )
        
        print(f"Server running at http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        
        server.run()
        return 0
        
    except KeyboardInterrupt:
        print("\nServer stopped")
        return 0
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1


def handle_client_list(args: argparse.Namespace) -> int:
    """Handle client list command."""
    try:
        client = connect(args.url)
        packages = client.list_packages()
        
        if packages:
            print("Available packages:")
            for package in sorted(packages):
                print(f"  - {package}")
        else:
            print("No packages available")
        
        return 0
        
    except Exception as e:
        print(f"Error listing packages: {e}")
        return 1


def handle_client_info(args: argparse.Namespace) -> int:
    """Handle client info command."""
    try:
        client = connect(args.url)
        info = client.get_package_info(args.package)
        
        print(f"Package: {args.package}")
        print(json.dumps(info, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error getting package info: {e}")
        return 1


def handle_client_stats(args: argparse.Namespace) -> int:
    """Handle client stats command."""
    try:
        client = connect(args.url)
        stats = client.get_stats()
        
        print("CDN Statistics:")
        print(json.dumps(stats, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return 1


def handle_deploy(args: argparse.Namespace) -> int:
    """Handle deploy command."""
    try:
        deployer = PackageDeployer(args.url)
        
        print(f"Deploying package: {args.package}")
        
        result = deployer.deploy_package(
            package_name=args.package,
            version=args.version
        )
        
        print("Deployment successful:")
        print(json.dumps(result, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"Error deploying package: {e}")
        return 1


def handle_test(args: argparse.Namespace) -> int:
    """Handle test command."""
    try:
        print(f"Testing connection to {args.url}")
        
        client = connect(args.url)
        
        # Test basic connectivity
        packages = client.list_packages()
        print(f"✓ Connection successful")
        print(f"✓ Found {len(packages)} packages")
        
        # Test stats
        stats = client.get_stats()
        print(f"✓ Server statistics available")
        
        print("\nServer info:")
        print(f"  URL: {args.url}")
        print(f"  Packages: {len(packages)}")
        
        if "server" in stats:
            server_stats = stats["server"]
            print(f"  Total executions: {server_stats.get('total_executions', 0)}")
            print(f"  Loaded packages: {server_stats.get('packages_loaded', 0)}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Enable debug mode if requested
    if args.debug:
        set_debug_mode(True)
        print("Debug mode enabled")
    
    # Handle commands
    if args.command == "server":
        if args.server_command == "start":
            return handle_server_start(args)
        else:
            print("Please specify a server command (start)")
            return 1
    
    elif args.command == "client":
        if args.client_command == "list":
            return handle_client_list(args)
        elif args.client_command == "info":
            return handle_client_info(args)
        elif args.client_command == "stats":
            return handle_client_stats(args)
        else:
            print("Please specify a client command (list, info, stats)")
            return 1
    
    elif args.command == "deploy":
        return handle_deploy(args)
    
    elif args.command == "test":
        return handle_test(args)
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 