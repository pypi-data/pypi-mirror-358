#!/usr/bin/env python3
"""
Unit tests for PyCDN server functionality.
"""

import unittest
import sys
import os
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pycdn.server.core import CDNServer, PackageDeployer
from pycdn.server.runtime import PackageRuntime, ExecutionEnvironment
from pycdn.utils.common import serialize_args, deserialize_args, serialize_result


class TestPackageRuntime(unittest.TestCase):
    """Test cases for PackageRuntime class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runtime = PackageRuntime()
    
    def test_runtime_initialization(self):
        """Test runtime initialization."""
        self.assertIsInstance(self.runtime.environments, dict)
        self.assertEqual(len(self.runtime.environments), 0)
        self.assertIsInstance(self.runtime.execution_stats, dict)
        self.assertEqual(self.runtime.execution_stats["total_executions"], 0)
    
    def test_get_environment(self):
        """Test getting execution environment."""
        env = self.runtime.get_environment("math")
        
        self.assertIsInstance(env, ExecutionEnvironment)
        self.assertEqual(env.package_name, "math")
        self.assertEqual(self.runtime.execution_stats["packages_loaded"], 1)
        
        # Getting same environment should return cached version
        env2 = self.runtime.get_environment("math")
        self.assertIs(env, env2)
        self.assertEqual(self.runtime.execution_stats["packages_loaded"], 1)
    
    @patch('importlib.import_module')
    def test_execute_remote_function_success(self, mock_import):
        """Test successful remote function execution."""
        # Mock math module
        mock_math = Mock()
        mock_math.sqrt.return_value = 4.0
        mock_import.return_value = mock_math
        
        # Prepare serialized arguments
        serialized_args = serialize_args(16)
        
        # Execute function
        result = self.runtime.execute_remote_function("math", "sqrt", serialized_args)
        
        # Verify result structure
        self.assertIn("result", result)
        self.assertIn("success", result)
        self.assertTrue(result["success"])
        
        # Verify stats updated
        self.assertEqual(self.runtime.execution_stats["total_executions"], 1)
        self.assertEqual(self.runtime.execution_stats["successful_executions"], 1)
        self.assertEqual(self.runtime.execution_stats["failed_executions"], 0)
    
    def test_execute_remote_function_failure(self):
        """Test failed remote function execution."""
        # Use non-existent package
        serialized_args = serialize_args()
        
        result = self.runtime.execute_remote_function("nonexistent", "func", serialized_args)
        
        # Verify error result
        self.assertIn("success", result)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Verify stats updated
        self.assertEqual(self.runtime.execution_stats["total_executions"], 1)
        self.assertEqual(self.runtime.execution_stats["successful_executions"], 0)
        self.assertEqual(self.runtime.execution_stats["failed_executions"], 1)
    
    @patch('importlib.import_module')
    def test_get_package_info(self, mock_import):
        """Test getting package information."""
        # Mock math module
        mock_math = Mock()
        mock_math.__version__ = "3.9.0"
        mock_math.__file__ = "/usr/lib/python3.9/lib-dynload/math.cpython-39.so"
        mock_math.sqrt = Mock()
        mock_math.pi = 3.14159
        mock_import.return_value = mock_math
        
        # Mock dir() function
        with patch('builtins.dir') as mock_dir:
            mock_dir.return_value = ["sqrt", "pi", "factorial", "__version__", "__file__"]
            
            info = self.runtime.get_package_info("math")
        
        # Verify package info
        self.assertEqual(info["package_name"], "math")
        self.assertEqual(info["version"], "3.9.0")
        self.assertTrue(info["loaded"])
        self.assertIn("attributes", info)
        
        # Check attributes
        attr_names = [attr["name"] for attr in info["attributes"]]
        self.assertIn("sqrt", attr_names)
        self.assertIn("pi", attr_names)
        self.assertIn("factorial", attr_names)


class TestExecutionEnvironment(unittest.TestCase):
    """Test cases for ExecutionEnvironment class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.env = ExecutionEnvironment("math")
    
    def test_environment_initialization(self):
        """Test environment initialization."""
        self.assertEqual(self.env.package_name, "math")
        self.assertEqual(self.env.security_level, "standard")
        self.assertIsInstance(self.env._loaded_modules, dict)
    
    @patch('importlib.import_module')
    def test_load_package(self, mock_import):
        """Test package loading."""
        mock_math = Mock()
        mock_import.return_value = mock_math
        
        self.env.load_package()
        
        # Verify module loaded
        mock_import.assert_called_once_with("math")
        self.assertIn("math", self.env._loaded_modules)
        self.assertEqual(self.env._loaded_modules["math"], mock_math)
    
    @patch('importlib.import_module')
    def test_get_function(self, mock_import):
        """Test getting function from package."""
        mock_math = Mock()
        mock_sqrt = Mock()
        mock_math.sqrt = mock_sqrt
        mock_import.return_value = mock_math
        
        func = self.env.get_function("sqrt")
        
        self.assertEqual(func, mock_sqrt)
    
    @patch('importlib.import_module')
    def test_execute_function(self, mock_import):
        """Test function execution."""
        mock_math = Mock()
        mock_sqrt = Mock(return_value=4.0)
        mock_math.sqrt = mock_sqrt
        mock_import.return_value = mock_math
        
        result = self.env.execute_function("sqrt", (16,), {})
        
        self.assertEqual(result, 4.0)
        mock_sqrt.assert_called_once_with(16)


class TestCDNServer(unittest.TestCase):
    """Test cases for CDNServer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = CDNServer(
            host="localhost",
            port=8000,
            debug=True,
            allowed_packages=["math", "json"]
        )
    
    def test_server_initialization(self):
        """Test server initialization."""
        self.assertEqual(self.server.host, "localhost")
        self.assertEqual(self.server.port, 8000)
        self.assertTrue(self.server.debug)
        self.assertEqual(self.server.allowed_packages, {"math", "json"})
        self.assertIsNotNone(self.server.app)
        self.assertIsNotNone(self.server.runtime)
    
    def test_add_allowed_package(self):
        """Test adding allowed package."""
        self.server.add_allowed_package("requests")
        
        self.assertIn("requests", self.server.allowed_packages)
    
    def test_remove_allowed_package(self):
        """Test removing allowed package."""
        self.server.remove_allowed_package("math")
        
        self.assertNotIn("math", self.server.allowed_packages)
    
    def test_get_allowed_packages(self):
        """Test getting allowed packages."""
        packages = self.server.get_allowed_packages()
        
        self.assertIsInstance(packages, set)
        self.assertEqual(packages, {"math", "json"})


class TestPackageDeployer(unittest.TestCase):
    """Test cases for PackageDeployer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.deployer = PackageDeployer("http://localhost:8000")
    
    def test_deployer_initialization(self):
        """Test deployer initialization."""
        self.assertEqual(self.deployer.server_url, "http://localhost:8000")
        self.assertIsInstance(self.deployer.deployed_packages, set)
    
    @patch('importlib.import_module')
    def test_deploy_package_success(self, mock_import):
        """Test successful package deployment."""
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        result = self.deployer.deploy_package(
            package_name="requests",
            version="2.28.0",
            dependencies=["urllib3", "certifi"],
            compute_requirements={"cpu": "1vcpu", "memory": "512MB"},
            edge_locations=["us-east", "eu-west"]
        )
        
        # Verify deployment result
        self.assertEqual(result["package_name"], "requests")
        self.assertEqual(result["version"], "2.28.0")
        self.assertEqual(result["status"], "deployed")
        self.assertEqual(result["dependencies"], ["urllib3", "certifi"])
        
        # Verify package added to deployed list
        self.assertIn("requests", self.deployer.deployed_packages)
    
    def test_deploy_package_failure(self):
        """Test failed package deployment."""
        with self.assertRaises(ImportError):
            self.deployer.deploy_package("nonexistent_package")
    
    def test_list_deployments(self):
        """Test listing deployments."""
        self.deployer.deployed_packages.add("math")
        self.deployer.deployed_packages.add("json")
        
        deployments = self.deployer.list_deployments()
        
        self.assertIsInstance(deployments, list)
        self.assertIn("math", deployments)
        self.assertIn("json", deployments)
    
    def test_undeploy_package(self):
        """Test undeploying package."""
        self.deployer.deployed_packages.add("test_package")
        
        result = self.deployer.undeploy_package("test_package")
        
        self.assertTrue(result)
        self.assertNotIn("test_package", self.deployer.deployed_packages)
        
        # Test undeploying non-existent package
        result = self.deployer.undeploy_package("nonexistent")
        self.assertFalse(result)


class TestServerAPI(unittest.TestCase):
    """Test cases for server API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server = CDNServer(
            host="localhost",
            port=8000,
            debug=True,
            allowed_packages=["math", "json"]
        )
        self.app = self.server.app
        
        # Import test client
        try:
            from fastapi.testclient import TestClient
            self.client = TestClient(self.app)
        except ImportError:
            self.skipTest("FastAPI test client not available")
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "PyCDN Server")
        self.assertEqual(data["version"], "0.1.0")
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
    
    @patch('pycdn.server.core.PackageRuntime.execute_remote_function')
    def test_execute_endpoint(self, mock_execute):
        """Test function execution endpoint."""
        # Mock successful execution
        mock_execute.return_value = {
            "result": json.dumps(4.0),
            "success": True,
            "serialization_method": "json"
        }
        
        # Prepare request
        request_data = {
            "package_name": "math",
            "function_name": "sqrt",
            "args": json.dumps([16]),
            "kwargs": json.dumps({}),
            "serialization_method": "json"
        }
        
        response = self.client.post("/execute", json=request_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
    
    def test_execute_endpoint_forbidden_package(self):
        """Test execution with forbidden package."""
        request_data = {
            "package_name": "forbidden_package",
            "function_name": "some_func",
            "args": json.dumps([]),
            "kwargs": json.dumps({}),
            "serialization_method": "json"
        }
        
        response = self.client.post("/execute", json=request_data)
        
        self.assertEqual(response.status_code, 403)
    
    def test_packages_endpoint(self):
        """Test packages list endpoint."""
        # Add some packages to runtime
        self.server.runtime.get_environment("math")
        self.server.runtime.get_environment("json")
        
        response = self.client.get("/packages")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    @patch('pycdn.server.core.PackageRuntime.get_package_info')
    def test_package_info_endpoint(self, mock_get_info):
        """Test package info endpoint."""
        # Mock package info
        mock_get_info.return_value = {
            "package_name": "math",
            "version": "3.9.0",
            "loaded": True,
            "attributes": []
        }
        
        response = self.client.get("/packages/math/info")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["package_name"], "math")
    
    def test_package_info_endpoint_forbidden(self):
        """Test package info endpoint with forbidden package."""
        response = self.client.get("/packages/forbidden_package/info")
        
        self.assertEqual(response.status_code, 403)
    
    def test_stats_endpoint(self):
        """Test statistics endpoint."""
        response = self.client.get("/stats")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_executions", data)
        self.assertIn("loaded_packages", data)
    
    def test_clear_cache_endpoint(self):
        """Test cache clearing endpoint."""
        response = self.client.delete("/cache")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 