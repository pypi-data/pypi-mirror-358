#!/usr/bin/env python3
"""
Data Science PyCDN Server Example
=================================

This example shows how to start a PyCDN server specifically configured
for data science packages and workflows.

Usage:
    python examples/server/data_science_server.py

Note: This example requires numpy, pandas, and matplotlib to be installed
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pycdn.server import CDNServer

def check_packages(packages):
    """Check if required packages are available."""
    missing = []
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing

def main():
    """Start data science focused PyCDN server."""
    print("🔬 Data Science PyCDN Server Example")
    print("=" * 45)
    
    # Data science and scientific computing packages
    data_science_packages = [
        # Core scientific computing
        "math",
        "statistics",
        "random",
        
        # Data manipulation (if available)
        "json",
        "csv",
        "datetime",
        "collections",
        
        # System utilities
        "os",
        "sys",
        "pathlib",
        "urllib",
        
        # Text processing
        "re",
        "string",
        
        # Utilities
        "itertools",
        "functools",
        "operator"
    ]
    
    # Optional packages (require installation)
    optional_packages = ["numpy", "pandas", "matplotlib"]
    
    # Check for optional packages
    missing = check_packages(optional_packages)
    
    if missing:
        print(f"⚠️  Optional packages not available: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        print(f"   Continuing with standard library packages only...\n")
    else:
        print("✅ All optional data science packages available!")
        data_science_packages.extend(optional_packages)
    
    print(f"📦 Configured packages ({len(data_science_packages)}):")
    for i, pkg in enumerate(data_science_packages, 1):
        print(f"   {i:2d}. {pkg}")
    
    print(f"\n🌐 Server Configuration:")
    print(f"   • Host: localhost")
    print(f"   • Port: 8001")  # Different port to avoid conflicts
    print(f"   • Debug: ON")
    print(f"   • CORS: Enabled")
    print(f"   • Focus: Data Science")
    
    # Create server instance
    server = CDNServer(
        host="localhost",
        port=8001,  # Use port 8001 for data science server
        debug=True,
        allowed_packages=data_science_packages
    )
    
    print(f"\n⚡ Starting data science server...")
    print(f"📡 Server URL: http://localhost:8001")
    print(f"🔬 Focus: Scientific computing and data analysis")
    print(f"🔧 Press Ctrl+C to stop\n")
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Data science server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 