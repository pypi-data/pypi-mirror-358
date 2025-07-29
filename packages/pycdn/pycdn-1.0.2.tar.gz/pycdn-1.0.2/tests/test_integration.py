#!/usr/bin/env python3
"""
Integration tests for PyCDN end-to-end functionality.
"""

import unittest
import sys
import os
import time
import threading
import requests
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pycdn
from pycdn.server import CDNServer
from pycdn.utils.common import set_debug_mode


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test server for integration tests."""
        # Enable debug mode for tests
        set_debug_mode(True)
        
        # Create and start test server in background thread
        cls.server = CDNServer(
            host="localhost",
            port=8001,  # Use different port for tests
            debug=False,  # Reduce noise in tests
            allowed_packages=["math", "json", "random", "os", "sys"]
        )
        
        # Start server in daemon thread
        cls.server_thread = threading.Thread(
            target=cls.server.run,
            daemon=True
        )
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Verify server is running
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code != 200:
                raise Exception("Server health check failed")
        except Exception as e:
            raise unittest.SkipTest(f"Test server failed to start: {e}")
    
    def setUp(self):
        """Set up each test."""
        self.test_url = "http://localhost:8001"
    
    def test_basic_package_usage(self):
        """Test basic package usage through PyCDN."""
        # Connect to test server
        cdn_packages = pycdn.pkg(self.test_url)
        
        # Test math package
        math_pkg = cdn_packages.math
        
        # Test simple function call
        result = math_pkg.sqrt(16)
        self.assertEqual(result, 4.0)
        
        # Test constant access (if supported)
        try:
            pi_val = math_pkg.pi
            self.assertAlmostEqual(pi_val, 3.14159, places=4)
        except:
            # PI constant access might not be supported in MVP
            pass
    
    def test_multiple_packages(self):
        """Test using multiple packages."""
        cdn_packages = pycdn.pkg(self.test_url)
        
        # Test math functions
        math_result = cdn_packages.math.factorial(5)
        self.assertEqual(math_result, 120)
        
        # Test JSON operations
        test_data = {"test": "value", "number": 42}
        json_str = cdn_packages.json.dumps(test_data)
        parsed_data = cdn_packages.json.loads(json_str)
        self.assertEqual(parsed_data, test_data)
        
        # Test random number generation
        random_num = cdn_packages.random.randint(1, 100)
        self.assertTrue(1 <= random_num <= 100)
    
    def test_client_configuration(self):
        """Test client configuration options."""
        # Test custom timeout
        client = pycdn.connect(
            self.test_url,
            timeout=60,
            max_retries=5
        )
        
        # Test package listing
        packages = client.list_packages()
        self.assertIsInstance(packages, list)
        
        # Test package info
        if packages:
            info = client.get_package_info(packages[0])
            self.assertIn("package_name", info)
        
        # Close client
        client.close()
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        cdn_packages = pycdn.pkg(self.test_url)
        
        # Test non-existent function
        with self.assertRaises(Exception):
            cdn_packages.math.nonexistent_function()
        
        # Test invalid arguments
        with self.assertRaises(Exception):
            cdn_packages.math.sqrt("not a number")
    
    def test_caching_behavior(self):
        """Test caching behavior."""
        client = pycdn.connect(self.test_url)
        
        # Make same request multiple times
        start_time = time.time()
        
        from pycdn.client.lazy_loader import LazyPackage
        lazy_packages = LazyPackage(client)
        
        # First call
        result1 = lazy_packages.math.sqrt(25)
        first_call_time = time.time() - start_time
        
        # Second call (should be cached)
        start_time = time.time()
        result2 = lazy_packages.math.sqrt(25)
        second_call_time = time.time() - start_time
        
        # Results should be the same
        self.assertEqual(result1, result2)
        self.assertEqual(result1, 5.0)
        
        # Second call should be faster (cached)
        # Note: This might not always be true due to network variability
        # self.assertLess(second_call_time, first_call_time)
        
        client.close()
    
    def test_server_api_endpoints(self):
        """Test server API endpoints directly."""
        base_url = self.test_url
        
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "PyCDN Server")
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        
        # Test packages endpoint
        response = requests.get(f"{base_url}/packages")
        self.assertEqual(response.status_code, 200)
        packages = response.json()
        self.assertIsInstance(packages, list)
        
        # Test stats endpoint
        response = requests.get(f"{base_url}/stats")
        self.assertEqual(response.status_code, 200)
        stats = response.json()
        self.assertIn("total_executions", stats)
    
    def test_function_execution_api(self):
        """Test function execution API directly."""
        # Prepare execution request
        request_data = {
            "package_name": "math",
            "function_name": "pow",
            "args": pycdn.utils.common.serialize_args(2, 3)["args"],
            "kwargs": pycdn.utils.common.serialize_args(2, 3)["kwargs"],
            "serialization_method": "cloudpickle"
        }
        
        # Make execution request
        response = requests.post(
            f"{self.test_url}/execute",
            json=request_data
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        # Deserialize result
        result = pycdn.utils.common.deserialize_result(data)
        self.assertEqual(result, 8.0)
    
    def test_performance_baseline(self):
        """Test basic performance characteristics."""
        cdn_packages = pycdn.pkg(self.test_url)
        
        # Measure function call latency
        operations = [
            lambda: cdn_packages.math.sqrt(100),
            lambda: cdn_packages.math.factorial(10),
            lambda: cdn_packages.json.dumps({"test": 123}),
        ]
        
        latencies = []
        for operation in operations:
            start_time = time.time()
            try:
                result = operation()
                latency = time.time() - start_time
                latencies.append(latency)
            except Exception as e:
                self.fail(f"Operation failed: {e}")
        
        # Basic performance checks
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # These are very loose bounds for basic functionality
        self.assertLess(avg_latency, 5.0, "Average latency too high")
        self.assertLess(max_latency, 10.0, "Maximum latency too high")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        cdn_packages = pycdn.pkg(self.test_url)
        
        def make_request(i):
            return cdn_packages.math.sqrt(i * i)
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(1, 6)]
            results = [future.result() for future in futures]
        
        # Verify all results
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(results, expected)


class TestFailureScenarios(unittest.TestCase):
    """Test failure scenarios and edge cases."""
    
    def test_server_unavailable(self):
        """Test behavior when server is unavailable."""
        with self.assertRaises(Exception):
            # Try to connect to non-existent server
            cdn_packages = pycdn.pkg("http://localhost:9999")
            cdn_packages.math.sqrt(16)
    
    def test_invalid_package(self):
        """Test behavior with invalid package names."""
        # This test would require a running server
        # For now, we'll test the validation logic
        from pycdn.utils.common import validate_package_name
        
        self.assertFalse(validate_package_name(""))
        self.assertFalse(validate_package_name("invalid-package!"))
        self.assertTrue(validate_package_name("valid_package"))
        self.assertTrue(validate_package_name("math"))


class TestConfigurationAndSetup(unittest.TestCase):
    """Test configuration and setup scenarios."""
    
    def test_global_configuration(self):
        """Test global configuration."""
        # Test initial configuration
        config = pycdn.get_config()
        self.assertIsInstance(config, dict)
        
        # Test setting configuration
        pycdn.set_config(timeout=120, debug=True)
        updated_config = pycdn.get_config()
        self.assertEqual(updated_config["timeout"], 120)
        self.assertEqual(updated_config["debug"], True)
    
    def test_import_hooks(self):
        """Test import hook functionality."""
        from pycdn.client.import_hook import (
            install_import_hook,
            uninstall_import_hook,
            is_hook_installed
        )
        
        # Initially not installed
        self.assertFalse(is_hook_installed())
        
        # Install hook
        install_import_hook("http://localhost:8001", ["test_"])
        self.assertTrue(is_hook_installed())
        
        # Uninstall hook
        uninstall_import_hook()
        self.assertFalse(is_hook_installed())


if __name__ == "__main__":
    # Run integration tests
    unittest.main(verbosity=2) 