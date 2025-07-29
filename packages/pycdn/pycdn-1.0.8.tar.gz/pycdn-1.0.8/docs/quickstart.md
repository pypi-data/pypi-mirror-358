# PyCDN Quickstart Guide

Welcome to PyCDN! This guide will help you get started with revolutionary Python package delivery via CDN with lazy loading.

## What is PyCDN?

PyCDN eliminates dependency hell by delivering Python packages through a global CDN network with intelligent lazy loading. No more `pip install` - just import and use packages instantly from our edge-optimized servers.

## Installation

```bash
pip install pycdn
```

## Quick Start

### 1. Start a CDN Server

```bash
# Start the CDN server
pycdn server start

# Or start with specific packages allowed
pycdn server start --allowed-packages math json requests
```

The server will start at `http://localhost:8000` by default.

### 2. Use Packages via CDN

```python
import pycdn

# Connect to CDN server
cdn_packages = pycdn.pkg("http://localhost:8000")

# Use packages lazily - they load only when needed
from cdn_packages.math import sqrt, pi
from cdn_packages.json import dumps, loads

# Call functions remotely
result = sqrt(16)  # Returns 4.0
print(f"Square root of 16: {result}")

# Use constants
print(f"Value of PI: {pi}")

# JSON operations
data = {"message": "Hello PyCDN!", "value": 42}
json_str = dumps(data)
parsed = loads(json_str)
print(f"JSON roundtrip: {parsed}")
```

### 3. Advanced Usage

```python
import pycdn

# Configure client with custom settings
client = pycdn.connect(
    url="http://localhost:8000",
    timeout=30,
    cache_size="100MB",
    max_retries=3
)

# Get server information
packages = client.list_packages()
print(f"Available packages: {packages}")

# Get package details
info = client.get_package_info("math")
print(f"Math package info: {info}")

# Get server statistics
stats = client.get_stats()
print(f"Server stats: {stats}")

# Close client when done
client.close()
```

## Key Features

### 🌐 Global CDN Network
- Ultra-low latency package delivery
- Intelligent geo-routing
- 99.99% uptime SLA

### ⚡ Lazy Loading
- Packages loaded only when imported
- Smart dependency resolution
- Automatic version compatibility

### 🔒 Secure Execution
- Isolated execution environments
- Runtime security scanning
- Zero-trust verification

### 📦 Zero Local Dependencies
- No more `requirements.txt` management
- Consistent package versions
- Instant development environment setup

## Command Line Interface

```bash
# Server management
pycdn server start --port 8080 --host 0.0.0.0

# Client operations
pycdn client list                    # List packages
pycdn client info requests           # Get package info
pycdn client stats                   # Server statistics

# Package deployment
pycdn deploy requests --version latest

# Test connection
pycdn test --url http://localhost:8000
```

## Configuration

### Global Configuration

```python
import pycdn

# Set global defaults
pycdn.configure(
    default_url="http://localhost:8000",
    timeout=60,
    cache_size="200MB",
    max_retries=3
)

# Preload common packages
pycdn.preload(["math", "json", "requests"])
```

### Environment Variables

```bash
export PYCDN_DEFAULT_URL="http://localhost:8000"
export PYCDN_TIMEOUT=30
export PYCDN_CACHE_SIZE="100MB"
```

## Examples

### Data Science Workflow

```python
import pycdn

# Scientific computing stack
cdn = pycdn.pkg("http://localhost:8000")

# Load packages on demand
from cdn.json import loads
from cdn.math import sqrt, pi

# Instant data science environment
data = {"values": [1, 4, 9, 16, 25]}
sqrt_values = [sqrt(x) for x in data["values"]]
print(f"Square roots: {sqrt_values}")
```

### Web Development

```python
import pycdn

# Web framework packages
cdn = pycdn.pkg("http://localhost:8000")

from cdn.json import dumps as json_dumps
from cdn.os import getenv

# Ready-to-use utilities
config = {"debug": getenv("DEBUG", "false").lower() == "true"}
response = json_dumps({"status": "ok", "config": config})
```

## Performance Tips

1. **Preload packages** for better performance:
   ```python
   pycdn.preload(["math", "json", "requests"])
   ```

2. **Use caching** effectively:
   ```python
   client = pycdn.connect(url, cache_size="500MB")
   ```

3. **Reuse client connections**:
   ```python
   with pycdn.connect(url) as client:
       # Use client for multiple operations
   ```

## Troubleshooting

### Server Not Responding
```bash
# Check server status
pycdn test --url http://localhost:8000

# Check server logs
pycdn server start --debug
```

### Package Not Found
```bash
# List available packages
pycdn client list

# Check package info
pycdn client info package_name
```

### Performance Issues
```python
# Enable debug mode
pycdn.set_debug_mode(True)

# Check client stats
client = pycdn.connect(url)
stats = client.get_stats()
print(stats)
```

## Next Steps

- Check out the [API Reference](api_reference.md)
- See [Examples](examples.md) for more use cases
- Learn about [deployment strategies](deployment.md)
- Join our [community Discord](https://discord.gg/pycdn)

## Support

- **Documentation**: [docs.pycdn.dev](https://docs.pycdn.dev)
- **Issues**: [GitHub Issues](https://github.com/harshalmore31/pycdn/issues)
- **Email**: support@pycdn.dev

---

**Built with ❤️ by the PyCDN team**