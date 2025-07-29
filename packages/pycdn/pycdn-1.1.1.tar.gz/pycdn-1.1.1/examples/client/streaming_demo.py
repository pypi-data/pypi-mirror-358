"""
PyCDN Streaming Demo - Runtime Environment with Terminal Output

This demo showcases PyCDN's advanced capabilities for handling packages
that have interactive CLI interfaces, generate terminal output, or need
real-time monitoring.

Features demonstrated:
1. Real-time output streaming from packages
2. Interactive CLI sessions 
3. Package monitoring and logging
4. Terminal forwarding capabilities
5. Progress tracking for long-running operations

Usage:
    # First start a server:
    python examples/server/basic_server.py
    
    # Then run this streaming demo:
    python examples/client/streaming_demo.py
"""

import sys
import os
import asyncio
import time
import threading
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pycdn
from pycdn.client.core import CDNClient


def custom_output_handler(stream_type: str, data: str):
    """Custom output handler with colored terminal output."""
    colors = {
        "stdout": "\033[92m",  # Green
        "stderr": "\033[91m",  # Red
        "error": "\033[93m",   # Yellow
        "reset": "\033[0m"     # Reset
    }
    
    color = colors.get(stream_type, colors["reset"])
    prefix = f"[{stream_type.upper()}]"
    
    print(f"{color}{prefix}{colors['reset']} {data}", end="")


def demo_basic_streaming():
    """Demo 1: Basic streaming output from packages"""
    print("\n" + "="*50)
    print("DEMO 1: Basic Streaming Output")
    print("="*50)
    
    try:
        # Connect to CDN server
        client = CDNClient("http://localhost:8000", debug=True)
        
        print("📡 Testing basic streaming with math operations...")
        
        # Call function with streaming output
        result = client.call_function(
            package_name="math",
            function_name="sqrt", 
            args=(16,),
            stream_output=True,
            output_handler=custom_output_handler
        )
        
        print(f"✅ Result: {result}")
        
        # Multiple operations with output
        print("\n📊 Running multiple operations with output capture...")
        
        operations = [
            ("math", "sqrt", (25,)),
            ("math", "factorial", (5,)),
            ("json", "dumps", ({"message": "Hello PyCDN!"},))
        ]
        
        for pkg, func, args in operations:
            print(f"\n🔄 Executing {pkg}.{func}{args}")
            result = client.call_function(
                package_name=pkg,
                function_name=func,
                args=args,
                stream_output=True,
                output_handler=custom_output_handler
            )
            print(f"📋 Result: {result}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Demo 1 failed: {e}")


def demo_package_monitoring():
    """Demo 2: Real-time package monitoring"""
    print("\n" + "="*50)
    print("DEMO 2: Real-time Package Monitoring")
    print("="*50)
    
    try:
        client = CDNClient("http://localhost:8000")
        
        print("📺 Starting real-time monitoring for 'os' package...")
        
        # Start monitoring
        monitor = client.monitor_package("os", custom_output_handler)
        
        # Simulate some operations while monitoring
        print("🔄 Performing operations while monitoring...")
        
        time.sleep(1)
        
        # Execute some functions that generate output
        client.call_function("os", "getcwd", ())
        time.sleep(0.5)
        
        client.call_function("os", "listdir", (".",))
        time.sleep(0.5)
        
        # Stop monitoring
        monitor.stop()
        print("\n✅ Monitoring stopped")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Demo 2 failed: {e}")


async def demo_interactive_session():
    """Demo 3: Interactive CLI session"""
    print("\n" + "="*50)
    print("DEMO 3: Interactive CLI Session")
    print("="*50)
    
    try:
        client = CDNClient("http://localhost:8000")
        
        print("🖥️  Starting interactive session for 'os' package...")
        
        with client.interactive_session("os") as session:
            print("💻 Session started! Executing commands...")
            
            # Execute some commands
            commands = [
                "pwd",
                "ls -la",
                "echo 'Hello from PyCDN interactive session!'",
                "python --version"
            ]
            
            for cmd in commands:
                print(f"\n$ {cmd}")
                return_code = await session.execute_command(cmd)
                print(f"[Exit code: {return_code}]")
                
                await asyncio.sleep(1)
        
        print("\n✅ Interactive session completed")
        client.close()
        
    except Exception as e:
        print(f"❌ Demo 3 failed: {e}")


def demo_progress_tracking():
    """Demo 4: Progress tracking for long operations"""
    print("\n" + "="*50)
    print("DEMO 4: Progress Tracking")
    print("="*50)
    
    try:
        client = CDNClient("http://localhost:8000")
        
        print("⏳ Simulating long-running operation with progress...")
        
        def progress_handler(stream_type: str, data: str):
            """Enhanced handler for progress tracking"""
            if "progress" in data.lower() or "%" in data:
                print(f"📊 Progress: {data.strip()}")
            else:
                custom_output_handler(stream_type, data)
        
        # Simulate a long operation (like downloading or processing)
        print("🔄 Starting simulated long operation...")
        
        # This would be a real long-running function in practice
        result = client.call_function(
            package_name="time",
            function_name="sleep",
            args=(2,),  # 2 second operation
            stream_output=True,
            output_handler=progress_handler
        )
        
        print(f"✅ Operation completed: {result}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Demo 4 failed: {e}")


def demo_concurrent_streaming():
    """Demo 5: Concurrent streaming from multiple packages"""
    print("\n" + "="*50)
    print("DEMO 5: Concurrent Streaming")
    print("="*50)
    
    try:
        client = CDNClient("http://localhost:8000")
        
        print("🚀 Starting concurrent operations with streaming...")
        
        def threaded_operation(pkg: str, func: str, args: tuple, thread_id: int):
            """Run operation in separate thread"""
            def thread_handler(stream_type: str, data: str):
                print(f"[Thread-{thread_id}] {stream_type}: {data}", end="")
            
            try:
                result = client.call_function(
                    package_name=pkg,
                    function_name=func,
                    args=args,
                    stream_output=True,
                    output_handler=thread_handler
                )
                print(f"[Thread-{thread_id}] ✅ Result: {result}")
                return result
            except Exception as e:
                print(f"[Thread-{thread_id}] ❌ Error: {e}")
                return None
        
        # Start multiple concurrent operations
        operations = [
            ("math", "sqrt", (144,), 1),
            ("os", "getcwd", (), 2),
            ("json", "dumps", ({"concurrent": True, "thread": 3},), 3)
        ]
        
        threads = []
        for pkg, func, args, tid in operations:
            thread = threading.Thread(
                target=threaded_operation,
                args=(pkg, func, args, tid)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all operations to complete
        for thread in threads:
            thread.join()
        
        print("\n✅ All concurrent operations completed")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Demo 5 failed: {e}")


def demo_server_stats_monitoring():
    """Demo 6: Server statistics and health monitoring"""
    print("\n" + "="*50)
    print("DEMO 6: Server Statistics Monitoring")
    print("="*50)
    
    try:
        client = CDNClient("http://localhost:8000")
        
        print("📊 Monitoring server statistics...")
        
        # Get initial stats
        stats = client.get_stats()
        print("\n📈 Initial Server Stats:")
        print(f"  • Requests served: {stats['server']['requests_served']}")
        print(f"  • Active sessions: {stats['server']['active_sessions']}")
        print(f"  • Cache hits: {stats['client_cache']['hits']}")
        print(f"  • Uptime: {stats['server']['uptime_seconds']:.1f}s")
        
        # Perform some operations
        print("\n🔄 Performing operations to generate activity...")
        
        for i in range(5):
            client.call_function("math", "sqrt", (i * i,))
            time.sleep(0.2)
        
        # Get updated stats
        updated_stats = client.get_stats()
        print("\n📈 Updated Server Stats:")
        print(f"  • Requests served: {updated_stats['server']['requests_served']}")
        print(f"  • Active sessions: {updated_stats['server']['active_sessions']}")
        print(f"  • Cache hits: {updated_stats['client_cache']['hits']}")
        print(f"  • Active connections: {updated_stats['server'].get('active_connections', 0)}")
        
        # Calculate differences
        req_diff = updated_stats['server']['requests_served'] - stats['server']['requests_served']
        print(f"\n📊 Activity Summary:")
        print(f"  • New requests: {req_diff}")
        print(f"  • Cache efficiency: {updated_stats['client_cache']['hits']}/{updated_stats['client_cache']['hits'] + updated_stats['client_cache']['misses']} hits")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Demo 6 failed: {e}")


def main():
    """Main demo runner"""
    print("🚀 PyCDN Streaming & Runtime Demo")
    print("="*50)
    print("This demo showcases PyCDN's advanced streaming capabilities")
    print("for packages with terminal output, CLI interfaces, and real-time monitoring.\n")
    
    # Check server availability
    try:
        client = CDNClient("http://localhost:8000", timeout=5)
        packages = client.list_packages()
        print(f"✅ Connected to PyCDN server")
        print(f"📦 Available packages: {packages}")
        client.close()
    except Exception as e:
        print(f"❌ Cannot connect to PyCDN server: {e}")
        print("Please ensure the server is running with: pycdn server start")
        return
    
    # Run demonstrations
    demos = [
        ("Basic Streaming Output", demo_basic_streaming),
        ("Package Monitoring", demo_package_monitoring),
        ("Interactive Session", lambda: asyncio.run(demo_interactive_session())),
        ("Progress Tracking", demo_progress_tracking),
        ("Concurrent Streaming", demo_concurrent_streaming),
        ("Server Statistics", demo_server_stats_monitoring)
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n🎯 Running: {demo_name}")
        try:
            demo_func()
            print(f"✅ {demo_name} completed successfully")
        except KeyboardInterrupt:
            print(f"\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ {demo_name} failed: {e}")
        
        time.sleep(1)  # Brief pause between demos
    
    print("\n" + "="*50)
    print("🎉 All streaming demos completed!")
    print("="*50)
    print("\nKey takeaways:")
    print("• PyCDN provides real-time output streaming")
    print("• Interactive CLI sessions work seamlessly")
    print("• Multiple packages can stream concurrently")
    print("• Complete monitoring and statistics available")
    print("• No local dependencies required!")


if __name__ == "__main__":
    main() 