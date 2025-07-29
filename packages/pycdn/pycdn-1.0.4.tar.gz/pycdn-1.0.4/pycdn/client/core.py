"""
Core client SDK for PyCDN package consumption.
"""

import os
import time
import threading
import queue
import json
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union, Callable
import httpx
from urllib.parse import urljoin, urlparse
import asyncio
import websockets
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .lazy_loader import LazyPackage, LazyModule
from ..utils.common import (
    serialize_args, deserialize_result, log_debug, parse_size, 
    deserialize_from_transport, serialize_for_transport, parse_cache_size
)


class CDNClient:
    """
    Main CDN client for connecting to PyCDN servers with streaming support.
    """
    
    def __init__(
        self,
        url: str,
        timeout: int = 30,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        cache_size: Union[str, int] = "50MB",
        max_retries: int = 3,
        debug: bool = False
    ):
        """
        Initialize CDN client.
        
        Args:
            url: CDN server URL
            timeout: Request timeout in seconds
            api_key: API key for authentication
            region: Preferred region
            cache_size: Local cache size
            max_retries: Maximum retry attempts
            debug: Enable debug mode
        """
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        self.region = region
        self.cache_size = parse_cache_size(cache_size)
        self.max_retries = max_retries
        self.debug = debug
        
        # Initialize HTTP client
        headers = {"User-Agent": "PyCDN-Client/0.1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        if region:
            headers["X-Region"] = region
            
        self.http_client = httpx.Client(
            timeout=timeout,
            headers=headers,
            follow_redirects=True
        )
        
        # Initialize caches and state
        self._response_cache = {}
        self._package_info_cache = {}
        self._connection_stats = {
            "requests_made": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
        
        # WebSocket connections
        self._ws_connections = {}
        self._output_handlers = {}
        self._running_streams = set()
        
        # Test connection
        self._test_connection()
        
        log_debug(f"CDN client initialized for {self.url}")
    
    def _test_connection(self) -> None:
        """Test connection to CDN server."""
        try:
            response = self.http_client.get(f"{self.url}/health")
            response.raise_for_status()
            log_debug("CDN server connection successful")
        except Exception as e:
            log_debug(f"CDN server connection test failed: {e}")
            # Don't raise error here, allow lazy connection
    
    def _execute_request(
        self,
        package_name: str,
        function_name: str,
        serialized_args: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Execute a remote function request.
        
        Args:
            package_name: Name of the package
            function_name: Name of the function
            serialized_args: Serialized function arguments
            
        Returns:
            Response dictionary
        """
        self._connection_stats["requests_made"] += 1
        
        # Check cache first
        cache_key = self._get_cache_key(package_name, function_name, serialized_args)
        if cache_key in self._response_cache:
            self._connection_stats["cache_hits"] += 1
            log_debug(f"Cache hit for {package_name}.{function_name}")
            return self._response_cache[cache_key]
        
        self._connection_stats["cache_misses"] += 1
        
        # Prepare request data
        request_data = {
            "package_name": package_name,
            "function_name": function_name,
            **serialized_args
        }
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                response = self.http_client.post(
                    f"{self.url}/execute",
                    json=request_data
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Cache successful responses
                if result.get("success", True):
                    self._cache_response(cache_key, result)
                
                return result
                
            except Exception as e:
                log_debug(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    self._connection_stats["errors"] += 1
                    raise ConnectionError(f"Failed to execute {package_name}.{function_name}: {e}")
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
    
    def _get_cache_key(
        self,
        package_name: str,
        function_name: str,
        serialized_args: Dict[str, str]
    ) -> str:
        """Generate cache key for request."""
        import hashlib
        key_data = f"{package_name}.{function_name}.{serialized_args['args']}.{serialized_args['kwargs']}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache a response."""
        # Simple cache management - in production would be more sophisticated
        if len(self._response_cache) > 1000:  # Simple limit
            # Remove oldest entries
            keys_to_remove = list(self._response_cache.keys())[:100]
            for key in keys_to_remove:
                del self._response_cache[key]
        
        self._response_cache[cache_key] = response
    
    def get_package_info(self, package_name: str) -> Dict[str, Any]:
        """
        Get information about a package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Package information dictionary
        """
        # Check cache first
        if package_name in self._package_info_cache:
            return self._package_info_cache[package_name]
        
        try:
            response = self.http_client.get(f"{self.url}/packages/{package_name}/info")
            response.raise_for_status()
            
            info = response.json()
            self._package_info_cache[package_name] = info
            return info
            
        except Exception as e:
            log_debug(f"Failed to get package info for {package_name}: {e}")
            return {"package_name": package_name, "error": str(e), "loaded": False}
    
    def list_packages(self) -> List[str]:
        """
        List all available packages on the CDN server.
        
        Returns:
            List of package names
        """
        try:
            response = self.http_client.get(f"{self.url}/packages")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log_debug(f"Failed to list packages: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get CDN server statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            response = self.http_client.get(f"{self.url}/stats")
            response.raise_for_status()
            server_stats = response.json()
            
            # Combine with client stats
            return {
                "server": server_stats,
                "client": self._connection_stats.copy()
            }
        except Exception as e:
            log_debug(f"Failed to get stats: {e}")
            return {"client": self._connection_stats.copy()}
    
    def clear_cache(self) -> None:
        """Clear local cache."""
        self._response_cache.clear()
        self._package_info_cache.clear()
        log_debug("Local cache cleared")
    
    def preload_packages(self, package_names: List[str]) -> None:
        """
        Preload package information.
        
        Args:
            package_names: List of package names to preload
        """
        for package_name in package_names:
            try:
                self.get_package_info(package_name)
                log_debug(f"Preloaded package info for {package_name}")
            except Exception as e:
                log_debug(f"Failed to preload {package_name}: {e}")
    
    def call_function(self, package_name: str, function_name: str, 
                     args: tuple = (), kwargs: dict = None, 
                     stream_output: bool = False, 
                     output_handler: Optional[Callable] = None) -> Any:
        """Call a function on the CDN server with optional output streaming."""
        if kwargs is None:
            kwargs = {}
            
        # Use regular execution for now (streaming can be added later)
        serialized_args = serialize_args(*args, **kwargs)
        result = self._execute_request(package_name, function_name, serialized_args)
        
        # Handle captured output if present
        if result.get("stdout"):
            print(result["stdout"], end="")
        if result.get("stderr"):
            print(result["stderr"], end="", file=__import__("sys").stderr)
        
        return deserialize_result(result)

    def close(self) -> None:
        """Close the HTTP client."""
        self.http_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global configuration
_global_client = None
_global_config = {
    "default_url": "http://localhost:8000",
    "timeout": 30,
    "cache_size": "100MB",
    "max_retries": 3
}


def pkg(url: str, **kwargs) -> LazyPackage:
    """
    Connect to a CDN server and return a lazy package namespace.
    
    Args:
        url: CDN server URL
        **kwargs: Additional client configuration
        
    Returns:
        LazyPackage instance
    """
    client = CDNClient(url, **kwargs)
    return LazyPackage(client)


def connect(url: str, **kwargs) -> CDNClient:
    """
    Create a new CDN client connection.
    
    Args:
        url: CDN server URL
        **kwargs: Additional client configuration
        
    Returns:
        CDNClient instance
    """
    return CDNClient(url, **kwargs)


def configure(**kwargs) -> None:
    """
    Configure global PyCDN settings.
    
    Args:
        **kwargs: Configuration options
    """
    global _global_config
    _global_config.update(kwargs)
    log_debug(f"Global configuration updated: {kwargs}")


def preload(packages: List[str], url: Optional[str] = None) -> None:
    """
    Preload packages from CDN server.
    
    Args:
        packages: List of package names to preload
        url: CDN server URL (uses global default if not specified)
    """
    global _global_client
    
    if url:
        client = CDNClient(url, **_global_config)
    else:
        if not _global_client:
            _global_client = CDNClient(_global_config["default_url"], **_global_config)
        client = _global_client
    
    client.preload_packages(packages)


def get_global_client() -> Optional[CDNClient]:
    """Get the global CDN client instance."""
    return _global_client


def set_global_client(client: CDNClient) -> None:
    """Set the global CDN client instance."""
    global _global_client
    _global_client = client 


class InteractiveSession:
    """Interactive session for CLI packages."""
    
    def __init__(self, base_url: str, package_name: str):
        self.base_url = base_url
        self.package_name = package_name
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.websocket = None
        self.session_id = None
        self._output_queue = queue.Queue()
        self._running = False

    async def _connect(self):
        """Connect to interactive session."""
        uri = f"{self.ws_url}/interactive/{self.package_name}"
        
        try:
            self.websocket = await websockets.connect(uri)
            
            # Wait for session start
            response = await self.websocket.recv()
            data = json.loads(response)
            
            if data["type"] == "session_start":
                self.session_id = data["session_id"]
                print(f"Interactive session started: {self.session_id}")
            
            self._running = True
            return True
            
        except Exception as e:
            print(f"Failed to start interactive session: {e}")
            return False

    async def execute_command(self, command: str, stream_output: bool = True):
        """Execute a command in the interactive session."""
        if not self.websocket:
            if not await self._connect():
                return False
        
        try:
            message = {
                "type": "command",
                "command": command
            }
            
            await self.websocket.send(json.dumps(message))
            
            if stream_output:
                while True:
                    response = await self.websocket.recv()
                    data = json.loads(response)
                    
                    if data["type"] == "stdout":
                        print(data["data"], end="")
                    elif data["type"] == "stderr":
                        print(data["data"], end="", file=__import__("sys").stderr)
                    elif data["type"] == "command_complete":
                        return data["return_code"]
                    elif data["type"] == "error":
                        print(f"Error: {data['message']}")
                        return -1
            
            return 0
            
        except Exception as e:
            print(f"Command execution failed: {e}")
            return -1

    def send_input(self, input_data: str):
        """Send input to the interactive process."""
        if self.websocket:
            message = {
                "type": "input",
                "data": input_data
            }
            asyncio.create_task(self.websocket.send(json.dumps(message)))

    def close(self):
        """Close the interactive session."""
        self._running = False
        if self.websocket:
            asyncio.create_task(self.websocket.close())


class PackageMonitor:
    """Monitor real-time output from a package."""
    
    def __init__(self, base_url: str, package_name: str, output_handler: Callable):
        self.base_url = base_url
        self.package_name = package_name
        self.output_handler = output_handler
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.websocket = None
        self._running = False
        self._thread = None

    def start(self):
        """Start monitoring."""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _monitor_loop(self):
        """Main monitoring loop."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        
        try:
            loop.run_until_complete(self._monitor())
        except Exception as e:
            print(f"Monitor error: {e}")
        finally:
            loop.close()

    async def _monitor(self):
        """Async monitoring function."""
        uri = f"{self.ws_url}/stream/{self.package_name}"
        
        try:
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                
                while self._running:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(response)
                        
                        if data["type"] in ["stdout", "stderr"]:
                            self.output_handler(data["type"], data["data"])
                        elif data["type"] == "output":
                            if data.get("stdout"):
                                self.output_handler("stdout", data["stdout"])
                            if data.get("stderr"):
                                self.output_handler("stderr", data["stderr"])
                        elif data["type"] == "error":
                            self.output_handler("error", data.get("error", "Unknown error"))
                            
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        await websocket.send(json.dumps({"type": "ping"}))
                    except websockets.exceptions.ConnectionClosed:
                        print(f"Connection to {self.package_name} monitor closed")
                        break
                        
        except Exception as e:
            print(f"Monitor connection failed: {e}")

    def call_function(self, package_name: str, function_name: str, 
                     args: tuple = (), kwargs: dict = None, 
                     stream_output: bool = False, 
                     output_handler: Optional[Callable] = None) -> Any:
        """Call a function on the CDN server with optional output streaming."""
        if kwargs is None:
            kwargs = {}
            
        # Check cache first
        cache_key = f"{package_name}.{function_name}:{hash((args, tuple(sorted(kwargs.items()))))}"
        if cache_key in self._response_cache:
            self._connection_stats["cache_hits"] += 1
            log_debug(f"Cache hit for {package_name}.{function_name}")
            return self._response_cache[cache_key]
        
        if stream_output and output_handler:
            return self._call_with_streaming(package_name, function_name, args, kwargs, output_handler)
        else:
            return self._call_regular(package_name, function_name, args, kwargs, cache_key)

    def _call_regular(self, package_name: str, function_name: str, 
                     args: tuple, kwargs: dict, cache_key: str) -> Any:
        """Regular HTTP API call without streaming."""
        try:
            payload = {
                "package_name": package_name,
                "function_name": function_name,
                "args": serialize_for_transport(args),
                "kwargs": serialize_for_transport(kwargs)
            }
            
            response = self.http_client.post(
                f"{self.url}/execute",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            result = deserialize_from_transport(data["result"])
            
            # Handle captured output
            if data.get("stdout"):
                print(data["stdout"], end="")
            if data.get("stderr"):
                print(data["stderr"], end="", file=__import__("sys").stderr)
            
            # Cache successful results
            self._response_cache[cache_key] = result
            self._connection_stats["cache_misses"] += 1
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to call {package_name}.{function_name}: {e}")
        except Exception as e:
            raise RuntimeError(f"Error executing {package_name}.{function_name}: {e}")

    def _call_with_streaming(self, package_name: str, function_name: str, 
                           args: tuple, kwargs: dict, 
                           output_handler: Callable) -> Any:
        """Call function with WebSocket streaming output."""
        import asyncio
        
        async def stream_call():
            ws_url = self.url.replace("http://", "ws://").replace("https://", "wss://")
            uri = f"{ws_url}/stream/{package_name}"
            
            try:
                async with websockets.connect(uri) as websocket:
                    # Send execution request
                    message = {
                        "type": "execute",
                        "package": package_name,
                        "function": function_name,
                        "args": args,
                        "kwargs": kwargs
                    }
                    
                    await websocket.send(json.dumps(message))
                    
                    result = None
                    while True:
                        try:
                            response = await websocket.recv()
                            data = json.loads(response)
                            
                            if data["type"] == "stdout":
                                output_handler("stdout", data["data"])
                            elif data["type"] == "stderr":
                                output_handler("stderr", data["data"])
                            elif data["type"] == "result":
                                result = deserialize_from_transport(data["data"])
                                break
                            elif data["type"] == "error":
                                raise RuntimeError(data["message"])
                                
                        except websockets.exceptions.ConnectionClosed:
                            break
                    
                    return result
                    
            except Exception as e:
                raise ConnectionError(f"WebSocket streaming failed: {e}")
        
        # Run async function in thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(stream_call())
        finally:
            loop.close()

    @contextmanager
    def interactive_session(self, package_name: str):
        """Create an interactive session for CLI packages."""
        session = InteractiveSession(self.url, package_name)
        try:
            yield session
        finally:
            session.close()

    def monitor_package(self, package_name: str, output_handler: Optional[Callable] = None):
        """Monitor real-time output from a package."""
        if output_handler is None:
            output_handler = self._default_output_handler
        
        monitor = PackageMonitor(self.url, package_name, output_handler)
        monitor.start()
        return monitor

    def _default_output_handler(self, stream_type: str, data: str):
        """Default output handler that prints to console."""
        if stream_type == "stdout":
            print(data, end="")
        elif stream_type == "stderr":
            print(data, end="", file=__import__("sys").stderr) 