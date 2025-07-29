"""
Core server SDK for PyCDN package deployment and serving.
"""

import os
import asyncio
import sys
import threading
import time
import traceback
import subprocess
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from typing import Any, Dict, List, Optional, Set
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json

from .runtime import PackageRuntime
from ..utils.common import log_debug, validate_package_name, serialize_for_transport, deserialize_from_transport


# Pydantic models for API requests/responses
class ExecuteRequest(BaseModel):
    """Request model for function execution."""
    package_name: str
    function_name: str
    args: str
    kwargs: str
    serialization_method: str = "json"


class ExecuteResponse(BaseModel):
    """Response model for function execution."""
    result: str
    success: bool
    serialization_method: str
    error: Optional[str] = None
    error_type: Optional[str] = None


class PackageInfo(BaseModel):
    """Model for package information."""
    package_name: str
    version: str = "unknown"
    file: str = "unknown"
    attributes: List[Dict[str, Any]] = []
    loaded: bool = False
    error: Optional[str] = None


class ServerStats(BaseModel):
    """Model for server statistics."""
    total_executions: int
    successful_executions: int
    failed_executions: int
    packages_loaded: int
    loaded_packages: List[str]


class PackageDeployer:
    """
    Package deployment manager for CDN servers.
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """
        Initialize package deployer.
        
        Args:
            server_url: URL of the CDN server
        """
        self.server_url = server_url
        self.deployed_packages: Set[str] = set()
        
    def deploy_package(
        self,
        package_name: str,
        version: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        compute_requirements: Optional[Dict[str, str]] = None,
        edge_locations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Deploy a package to the CDN server.
        
        Args:
            package_name: Name of the package to deploy
            version: Package version
            dependencies: List of package dependencies
            compute_requirements: Compute resource requirements
            edge_locations: List of edge locations to deploy to
            
        Returns:
            Deployment result dictionary
        """
        if not validate_package_name(package_name):
            raise ValueError(f"Invalid package name: {package_name}")
        
        log_debug(f"Deploying package {package_name} to {self.server_url}")
        
        # For MVP, we simulate deployment by checking if package can be imported
        try:
            import importlib
            importlib.import_module(package_name)
            
            deployment_info = {
                "package_name": package_name,
                "version": version or "latest",
                "server_url": self.server_url,
                "dependencies": dependencies or [],
                "compute_requirements": compute_requirements or {"cpu": "1vcpu", "memory": "512MB"},
                "edge_locations": edge_locations or ["local"],
                "status": "deployed",
                "deployed_at": None  # Would be timestamp in production
            }
            
            self.deployed_packages.add(package_name)
            return deployment_info
            
        except ImportError as e:
            raise ImportError(f"Cannot deploy package {package_name}: {e}")
    
    def list_deployments(self) -> List[str]:
        """List all deployed packages."""
        return list(self.deployed_packages)
    
    def undeploy_package(self, package_name: str) -> bool:
        """
        Undeploy a package from the CDN server.
        
        Args:
            package_name: Name of the package to undeploy
            
        Returns:
            True if successful
        """
        if package_name in self.deployed_packages:
            self.deployed_packages.remove(package_name)
            log_debug(f"Undeployed package: {package_name}")
            return True
        return False


class CDNServer:
    """
    Main CDN server for serving Python packages.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8000,
        debug: bool = False,
        allowed_packages: Optional[List[str]] = None
    ):
        """
        Initialize CDN server.
        
        Args:
            host: Server host
            port: Server port
            debug: Enable debug mode
            allowed_packages: List of allowed packages (None for all)
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.allowed_packages = set(allowed_packages) if allowed_packages else None
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="PyCDN Server",
            description="CDN server for Python package delivery with lazy loading",
            version="0.1.0",
            debug=debug
        )
        
        # Initialize package runtime
        self.runtime = PackageRuntime(allowed_packages=allowed_packages)
        
        # WebSocket connections for streaming output
        self.active_connections: Set[WebSocket] = set()
        self.session_streams: Dict[str, List[WebSocket]] = {}
        
        self.stats = {
            "requests_served": 0,
            "packages_loaded": 0,
            "cache_hits": 0,
            "errors": 0,
            "active_sessions": 0,
            "start_time": time.time()
        }
        
        # Setup routes
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            return {
                "message": "PyCDN Server",
                "version": "0.1.0",
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "server": "pycdn"}
        
        @self.app.post("/execute", response_model=ExecuteResponse)
        async def execute_function(request: ExecuteRequest):
            """Execute a function on a package."""
            
            # Validate package access
            if self.allowed_packages and request.package_name not in self.allowed_packages:
                raise HTTPException(
                    status_code=403,
                    detail=f"Package {request.package_name} not allowed"
                )
            
            # Execute function
            serialized_args = {
                "args": request.args,
                "kwargs": request.kwargs,
                "serialization_method": request.serialization_method
            }
            
            result = self.runtime.execute_remote_function(
                request.package_name,
                request.function_name,
                serialized_args
            )
            
            return ExecuteResponse(**result)
        
        @self.app.get("/packages/{package_name}/info", response_model=PackageInfo)
        async def get_package_info(package_name: str):
            """Get information about a package."""
            
            if self.allowed_packages and package_name not in self.allowed_packages:
                raise HTTPException(
                    status_code=403,
                    detail=f"Package {package_name} not allowed"
                )
            
            info = self.runtime.get_package_info(package_name)
            return PackageInfo(**info)
        
        @self.app.get("/packages", response_model=List[str])
        async def list_packages():
            """List all loaded packages."""
            return self.runtime.list_loaded_packages()
        
        @self.app.get("/stats", response_model=ServerStats)
        async def get_stats():
            """Get server statistics."""
            stats = self.runtime.get_execution_stats()
            stats["loaded_packages"] = self.runtime.list_loaded_packages()
            return ServerStats(**stats)
        
        @self.app.delete("/packages/{package_name}/cache")
        async def clear_package_cache(package_name: str):
            """Clear cache for a specific package."""
            self.runtime.clear_cache(package_name)
            return {"message": f"Cache cleared for {package_name}"}
        
        @self.app.delete("/cache")
        async def clear_all_cache():
            """Clear all package cache."""
            self.runtime.clear_cache()
            return {"message": "All cache cleared"}
        
        @self.app.websocket("/stream/{package_name}")
        async def websocket_stream(websocket: WebSocket, package_name: str):
            """WebSocket endpoint for real-time output streaming"""
            await websocket.accept()
            self.active_connections.add(websocket)
            
            if package_name not in self.session_streams:
                self.session_streams[package_name] = []
            self.session_streams[package_name].append(websocket)
            
            self.stats["active_sessions"] += 1
            
            try:
                # Send initial connection message
                await websocket.send_json({
                    "type": "connected",
                    "package": package_name,
                    "message": f"Connected to {package_name} output stream"
                })
                
                # Keep connection alive and handle client messages
                while True:
                    try:
                        data = await websocket.receive_text()
                        message = json.loads(data)
                        
                        # Handle different message types
                        if message.get("type") == "execute":
                            # Execute with streaming output
                            await self._execute_with_stream(websocket, message)
                        elif message.get("type") == "ping":
                            await websocket.send_json({"type": "pong"})
                            
                    except json.JSONDecodeError:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid JSON message"
                        })
                        
            except WebSocketDisconnect:
                pass
            finally:
                self.active_connections.discard(websocket)
                if package_name in self.session_streams:
                    if websocket in self.session_streams[package_name]:
                        self.session_streams[package_name].remove(websocket)
                    if not self.session_streams[package_name]:
                        del self.session_streams[package_name]
                self.stats["active_sessions"] -= 1

        @self.app.websocket("/interactive/{package_name}")
        async def interactive_session(websocket: WebSocket, package_name: str):
            """WebSocket endpoint for interactive CLI sessions"""
            await websocket.accept()
            
            try:
                # Create an interactive session
                session_id = f"{package_name}_{int(time.time())}"
                
                await websocket.send_json({
                    "type": "session_start",
                    "session_id": session_id,
                    "package": package_name
                })
                
                # Handle interactive commands
                while True:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message.get("type") == "command":
                        await self._handle_interactive_command(websocket, package_name, message)
                    elif message.get("type") == "input":
                        # Handle user input for interactive programs
                        await self._send_input_to_process(websocket, session_id, message["data"])
                        
            except WebSocketDisconnect:
                # Clean up session
                pass

        @self.app.get("/stats")
        async def get_stats():
            uptime = time.time() - self.stats["start_time"]
            return {
                **self.stats,
                "uptime_seconds": uptime,
                "active_connections": len(self.active_connections)
            }
    
    def run(self, **kwargs) -> None:
        """
        Run the CDN server.
        
        Args:
            **kwargs: Additional arguments for uvicorn
        """
        config = {
            "host": self.host,
            "port": self.port,
            "log_level": "debug" if self.debug else "info",
            **kwargs
        }
        
        log_debug(f"Starting CDN server at {self.host}:{self.port}")
        uvicorn.run(self.app, **config)
    
    async def start_async(self, **kwargs) -> None:
        """
        Start server asynchronously.
        
        Args:
            **kwargs: Additional arguments for uvicorn config
        """
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="debug" if self.debug else "info",
            **kwargs
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    def add_allowed_package(self, package_name: str) -> None:
        """
        Add a package to the allowed list.
        
        Args:
            package_name: Name of the package to allow
        """
        if self.allowed_packages is None:
            self.allowed_packages = set()
        self.allowed_packages.add(package_name)
    
    def remove_allowed_package(self, package_name: str) -> None:
        """
        Remove a package from the allowed list.
        
        Args:
            package_name: Name of the package to remove
        """
        if self.allowed_packages and package_name in self.allowed_packages:
            self.allowed_packages.remove(package_name)
    
    def get_allowed_packages(self) -> Optional[Set[str]]:
        """Get list of allowed packages."""
        return self.allowed_packages.copy() if self.allowed_packages else None

    async def _broadcast_output(self, package_name: str, message: Dict):
        """Broadcast output to all connected WebSocket clients for a package"""
        if package_name in self.session_streams:
            dead_connections = []
            for websocket in self.session_streams[package_name]:
                try:
                    await websocket.send_json(message)
                except:
                    dead_connections.append(websocket)
            
            # Clean up dead connections
            for conn in dead_connections:
                self.session_streams[package_name].remove(conn)
                self.active_connections.discard(conn)

    async def _execute_with_stream(self, websocket: WebSocket, message: Dict):
        """Execute function with real-time output streaming"""
        try:
            package_name = message["package"]
            function_name = message["function"]
            args = message.get("args", [])
            kwargs = message.get("kwargs", {})
            
            # Create output capture
            output_buffer = StringIO()
            error_buffer = StringIO()
            
            # Stream start notification
            await websocket.send_json({
                "type": "execution_start",
                "function": function_name,
                "package": package_name
            })
            
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                result = self.runtime.execute_function(package_name, function_name, args, kwargs)
            
            # Send captured output
            stdout_content = output_buffer.getvalue()
            stderr_content = error_buffer.getvalue()
            
            if stdout_content:
                await websocket.send_json({
                    "type": "stdout",
                    "data": stdout_content
                })
            
            if stderr_content:
                await websocket.send_json({
                    "type": "stderr", 
                    "data": stderr_content
                })
            
            # Send result
            await websocket.send_json({
                "type": "result",
                "data": serialize_for_transport(result),
                "function": function_name
            })
            
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "traceback": traceback.format_exc() if self.debug else None
            })

    async def _handle_interactive_command(self, websocket: WebSocket, package_name: str, message: Dict):
        """Handle interactive CLI commands"""
        try:
            command = message["command"]
            
            # Execute command in subprocess for better control
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            # Stream output in real-time
            async def stream_output():
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    await websocket.send_json({
                        "type": "stdout",
                        "data": line.decode()
                    })
            
            async def stream_errors():
                while True:
                    line = await process.stderr.readline()
                    if not line:
                        break
                    await websocket.send_json({
                        "type": "stderr",
                        "data": line.decode()
                    })
            
            # Start streaming tasks
            await asyncio.gather(stream_output(), stream_errors())
            
            # Wait for process completion
            return_code = await process.wait()
            
            await websocket.send_json({
                "type": "command_complete",
                "return_code": return_code
            })
            
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Command execution failed: {str(e)}"
            })

    async def _send_input_to_process(self, websocket: WebSocket, session_id: str, input_data: str):
        """Send input to interactive process"""
        # This would need session management for persistent processes
        # Implementation depends on specific requirements
        pass 