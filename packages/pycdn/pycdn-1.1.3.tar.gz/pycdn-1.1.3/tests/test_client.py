#!/usr/bin/env python3
"""
Unit tests for PyCDN client functionality.
"""

import unittest
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pycdn.client.core import CDNClient, pkg, connect, configure
from pycdn.client.lazy_loader import LazyPackage, LazyModule, LazyFunction
from pycdn.utils.common import serialize_args, deserialize_result, serialize_result


class TestCDNClient(unittest.TestCase):
    """Test cases for CDNClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_url = "http://test.example.com"
        self.mock_response_data = {
            "result": "test_result",
            "success": True,
            "serialization_method": "json"
        }
    
    @patch('pycdn.client.core.httpx.Client')
    def test_cdn_client_initialization(self, mock_httpx):
        """Test CDN client initialization."""
        # Mock HTTP client
        mock_client = Mock()
        mock_httpx.return_value = mock_client
        
        # Mock health check response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        
        # Create client
        client = CDNClient(
            url=self.test_url,
            timeout=30,
            api_key="test-key",
            region="us-east-1"
        )
        
        # Verify initialization
        self.assertEqual(client.url, self.test_url)
        self.assertEqual(client.timeout, 30)
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.region, "us-east-1")
        
        # Verify HTTP client setup
        mock_httpx.assert_called_once()
        args, kwargs = mock_httpx.call_args
        self.assertEqual(kwargs['timeout'], 30)
        self.assertIn("Authorization", kwargs['headers'])
        self.assertIn("X-Region", kwargs['headers'])
    
    @patch('pycdn.client.core.httpx.Client')
    def test_execute_request(self, mock_httpx):
        """Test remote function execution."""
        # Mock HTTP client
        mock_client = Mock()
        mock_httpx.return_value = mock_client
        
        # Mock responses
        health_response = Mock()
        health_response.raise_for_status.return_value = None
        
        execute_response = Mock()
        execute_response.raise_for_status.return_value = None
        execute_response.json.return_value = self.mock_response_data
        
        mock_client.get.return_value = health_response
        mock_client.post.return_value = execute_response
        
        # Create client
        client = CDNClient(self.test_url)
        
        # Test function execution
        serialized_args = serialize_args(1, 2, test="value")
        result = client._execute_request("math", "add", serialized_args)
        
        # Verify result
        self.assertEqual(result, self.mock_response_data)
        
        # Verify HTTP call
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        self.assertEqual(args[0], f"{self.test_url}/execute")
        
        request_data = kwargs['json']
        self.assertEqual(request_data['package_name'], "math")
        self.assertEqual(request_data['function_name'], "add")
    
    @patch('pycdn.client.core.httpx.Client')
    def test_get_package_info(self, mock_httpx):
        """Test getting package information."""
        # Mock HTTP client
        mock_client = Mock()
        mock_httpx.return_value = mock_client
        
        # Mock responses
        health_response = Mock()
        health_response.raise_for_status.return_value = None
        
        package_info = {
            "package_name": "math",
            "version": "3.9.0",
            "loaded": True,
            "attributes": [
                {"name": "sqrt", "type": "function", "callable": True},
                {"name": "pi", "type": "float", "callable": False}
            ]
        }
        
        info_response = Mock()
        info_response.raise_for_status.return_value = None
        info_response.json.return_value = package_info
        
        mock_client.get.side_effect = [health_response, info_response]
        
        # Create client and get package info
        client = CDNClient(self.test_url)
        result = client.get_package_info("math")
        
        # Verify result
        self.assertEqual(result, package_info)
        self.assertEqual(result["package_name"], "math")
        self.assertTrue(result["loaded"])
    
    @patch('pycdn.client.core.httpx.Client')
    def test_caching(self, mock_httpx):
        """Test response caching functionality."""
        # Mock HTTP client
        mock_client = Mock()
        mock_httpx.return_value = mock_client
        
        # Mock responses
        health_response = Mock()
        health_response.raise_for_status.return_value = None
        
        execute_response = Mock()
        execute_response.raise_for_status.return_value = None
        execute_response.json.return_value = self.mock_response_data
        
        mock_client.get.return_value = health_response
        mock_client.post.return_value = execute_response
        
        # Create client
        client = CDNClient(self.test_url)
        
        # Execute same request twice
        serialized_args = serialize_args(1, 2)
        result1 = client._execute_request("math", "add", serialized_args)
        result2 = client._execute_request("math", "add", serialized_args)
        
        # Verify both calls return same result
        self.assertEqual(result1, self.mock_response_data)
        self.assertEqual(result2, self.mock_response_data)
        
        # Verify HTTP client was called only once (second was cached)
        self.assertEqual(mock_client.post.call_count, 1)
        
        # Verify cache stats
        stats = client._connection_stats
        self.assertEqual(stats["cache_hits"], 1)
        self.assertEqual(stats["cache_misses"], 1)


class TestLazyLoader(unittest.TestCase):
    """Test cases for lazy loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client.url = "http://test.example.com"
        self.mock_client.get_package_info.return_value = {
            "package_name": "math",
            "attributes": [
                {"name": "sqrt", "type": "function", "callable": True},
                {"name": "pi", "type": "float", "callable": False}
            ]
        }
    
    def test_lazy_package_creation(self):
        """Test lazy package creation."""
        lazy_pkg = LazyPackage(self.mock_client)
        
        # Test package access
        math_module = lazy_pkg.math
        self.assertIsInstance(math_module, LazyModule)
        self.assertEqual(math_module._package_name, "math")
        self.assertEqual(math_module._cdn_client, self.mock_client)
    
    def test_lazy_module_creation(self):
        """Test lazy module creation."""
        lazy_module = LazyModule(self.mock_client, "math")
        
        # Verify module properties
        self.assertEqual(lazy_module.__name__, "math")
        self.assertEqual(lazy_module._package_name, "math")
        self.assertEqual(lazy_module._cdn_client, self.mock_client)
    
    def test_lazy_function_creation(self):
        """Test lazy function creation and execution."""
        # Mock client execution
        self.mock_client._execute_request.return_value = {
            "result": "4.0",
            "success": True,
            "serialization_method": "json"
        }
        
        # Create lazy function
        lazy_func = LazyFunction(
            self.mock_client,
            "math",
            "sqrt",
            "math.sqrt"
        )
        
        # Test function call
        with patch('pycdn.client.lazy_loader.deserialize_result') as mock_deserialize:
            mock_deserialize.return_value = 4.0
            result = lazy_func(16)
        
        # Verify result
        self.assertEqual(result, 4.0)
        
        # Verify client was called
        self.mock_client._execute_request.assert_called_once()
    
    def test_lazy_module_attribute_access(self):
        """Test lazy module attribute access."""
        lazy_module = LazyModule(self.mock_client, "math")
        
        # Test function attribute access
        sqrt_func = lazy_module.sqrt
        self.assertIsInstance(sqrt_func, LazyFunction)
        self.assertEqual(sqrt_func._function_name, "sqrt")


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_pkg_function(self):
        """Test pkg() convenience function."""
        with patch('pycdn.client.core.CDNClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            result = pkg("http://test.example.com", timeout=60)
            
            # Verify client creation
            mock_client_class.assert_called_once_with("http://test.example.com", timeout=60)
            self.assertIsInstance(result, LazyPackage)
    
    def test_connect_function(self):
        """Test connect() convenience function."""
        with patch('pycdn.client.core.CDNClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            result = connect("http://test.example.com", timeout=30)
            
            # Verify client creation
            mock_client_class.assert_called_once_with("http://test.example.com", timeout=30)
            self.assertEqual(result, mock_client)
    
    def test_configure_function(self):
        """Test configure() global configuration function."""
        # Import module to get initial config
        from pycdn.client.core import _global_config
        
        initial_timeout = _global_config.get("timeout", 30)
        
        # Configure new settings
        configure(timeout=60, cache_size="200MB")
        
        # Verify configuration updated
        self.assertEqual(_global_config["timeout"], 60)
        self.assertEqual(_global_config["cache_size"], "200MB")


class TestSerialization(unittest.TestCase):
    """Test cases for serialization/deserialization."""
    
    def test_serialize_args(self):
        """Test argument serialization."""
        args = (1, 2, "test")
        kwargs = {"key": "value", "number": 42}
        
        result = serialize_args(*args, **kwargs)
        
        # Verify result structure
        self.assertIn("args", result)
        self.assertIn("kwargs", result)
        self.assertIn("serialization_method", result)
    
    def test_serialize_result(self):
        """Test result serialization."""
        test_result = {"message": "success", "data": [1, 2, 3]}
        
        result = serialize_result(test_result)
        
        # Verify result structure
        self.assertIn("result", result)
        self.assertIn("success", result)
        self.assertIn("serialization_method", result)
        self.assertTrue(result["success"])
    
    def test_deserialize_result(self):
        """Test result deserialization."""
        # Test successful result
        serialized = {
            "result": json.dumps({"test": "value"}),
            "success": True,
            "serialization_method": "json"
        }
        
        result = deserialize_result(serialized)
        self.assertEqual(result, {"test": "value"})
        
        # Test error result
        error_serialized = {
            "success": False,
            "error": "Test error",
            "error_type": "ValueError"
        }
        
        with self.assertRaises(RuntimeError):
            deserialize_result(error_serialized)


class TestIntegration(unittest.TestCase):
    """Integration tests for PyCDN client."""
    
    @patch('pycdn.client.core.httpx.Client')
    def test_end_to_end_flow(self, mock_httpx):
        """Test complete end-to-end client flow."""
        # Mock HTTP client
        mock_client = Mock()
        mock_httpx.return_value = mock_client
        
        # Mock health check
        health_response = Mock()
        health_response.raise_for_status.return_value = None
        
        # Mock package info response
        info_response = Mock()
        info_response.raise_for_status.return_value = None
        info_response.json.return_value = {
            "package_name": "math",
            "attributes": [{"name": "sqrt", "type": "function", "callable": True}]
        }
        
        # Mock function execution response
        exec_response = Mock()
        exec_response.raise_for_status.return_value = None
        exec_response.json.return_value = {
            "result": json.dumps(4.0),
            "success": True,
            "serialization_method": "json"
        }
        
        # Setup mock responses
        mock_client.get.side_effect = [health_response, info_response]
        mock_client.post.return_value = exec_response
        
        # Run end-to-end test
        cdn_packages = pkg("http://test.example.com")
        math_module = cdn_packages.math
        sqrt_func = math_module.sqrt
        result = sqrt_func(16)
        
        # Verify result
        self.assertEqual(result, 4.0)
        
        # Verify HTTP calls were made
        self.assertTrue(mock_client.get.called)
        self.assertTrue(mock_client.post.called)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2) 