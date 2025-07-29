# PyCDN Examples

This directory contains comprehensive examples demonstrating PyCDN server and client functionality. The examples are organized into two main categories:

## 📁 Structure

```
examples/
├── server/          # Server setup examples
│   ├── basic_server.py       # Basic server with common packages
│   ├── data_science_server.py # Data science focused server
│   └── advanced_server.py    # Advanced server with deployment
├── client/          # Client usage examples
│   ├── basic_usage.py        # Basic client operations
│   ├── client_example.py     # Comprehensive client demo
│   ├── streaming_demo.py     # Real-time streaming features
│   └── openai_example.py     # OpenAI integration example
└── README.md        # This file
```

## 🚀 Quick Start

### Step 1: Start a Server

Choose one of the server examples and start it:

```bash
# Basic server (recommended for beginners)
python examples/server/basic_server.py

# OR data science server (if you have numpy, pandas installed)  
python examples/server/data_science_server.py

# OR advanced server with deployment features
python examples/server/advanced_server.py
```

The server will start at `http://localhost:8000` (or `8001` for data science).

### Step 2: Run Client Examples

In a **new terminal**, run any client example:

```bash
# Basic usage - great for beginners
python examples/client/basic_usage.py

# Comprehensive client demo
python examples/client/client_example.py

# Real-time streaming demo
python examples/client/streaming_demo.py

# OpenAI integration (requires API key)
python examples/client/openai_example.py
```

## 📊 Server Examples

### 🔰 Basic Server (`basic_server.py`)
**Perfect for beginners**
- Serves 18 common Python packages
- Runs on `localhost:8000`
- Includes math, json, time, random, etc.
- CORS enabled for web clients

```bash
python examples/server/basic_server.py
```

**Available packages:**
- `math`, `os`, `sys`, `json`, `time`, `datetime`
- `random`, `string`, `re`, `collections`, `itertools`
- `functools`, `operator`, `pathlib`, `urllib`, `base64`, `hashlib`, `uuid`

### 🔬 Data Science Server (`data_science_server.py`)
**For data science workflows**
- Includes scientific computing packages
- Automatically detects numpy, pandas, matplotlib
- Runs on `localhost:8001` to avoid conflicts
- Falls back gracefully if packages not installed

```bash
python examples/server/data_science_server.py
```

**Packages:** Standard library + numpy, pandas, matplotlib (if available)

### ⚡ Advanced Server (`advanced_server.py`)
**For advanced use cases**
- Package deployment examples
- Async server operations
- Multiple server modes
- Server management features

```bash
# Regular server mode
python examples/server/advanced_server.py

# Package deployment demo
python examples/server/advanced_server.py --mode deploy

# Async server demo
python examples/server/advanced_server.py --mode async
```

## 📱 Client Examples

### 🔰 Basic Usage (`basic_usage.py`)
**Perfect for beginners**
- Three different usage patterns
- Package access via `pycdn.pkg()`
- Direct client configuration
- Import hook demonstration

```bash
python examples/client/basic_usage.py
```

**Features demonstrated:**
- Quick package access
- Client configuration
- Function calls
- Statistics and caching

### 📡 Client Example (`client_example.py`)
**Comprehensive client demo**
- Full client API demonstration
- Error handling examples
- Performance testing
- Advanced configuration

```bash
python examples/client/client_example.py
```

### 🌊 Streaming Demo (`streaming_demo.py`)
**Real-time streaming features**
- WebSocket-based output streaming
- Interactive CLI sessions
- Concurrent package monitoring
- Real-time progress tracking

```bash
python examples/client/streaming_demo.py
```

**Features demonstrated:**
- Live output streaming
- Interactive sessions
- Progress monitoring
- Concurrent operations

### 🤖 OpenAI Example (`openai_example.py`)
**AI integration demo**
- OpenAI API integration
- Remote AI model access
- Secure API key handling
- AI-powered code generation

```bash
# Set your OpenAI API key first
export OPENAI_API_KEY="your-key-here"
python examples/client/openai_example.py
```

## 🔧 Configuration

### Server Configuration
Servers can be configured with:
- **Host/Port**: Change server address
- **Allowed Packages**: Control which packages are available
- **Debug Mode**: Enable detailed logging
- **CORS**: Configure cross-origin requests

```python
server = CDNServer(
    host="localhost",
    port=8000,
    debug=True,
    allowed_packages=["math", "json", "time"]
)
```

### Client Configuration
Clients support:
- **Timeout**: Request timeout settings
- **Cache Size**: Local caching configuration
- **Retries**: Automatic retry logic
- **Debug Mode**: Detailed logging

```python
client = pycdn.connect(
    url="http://localhost:8000",
    timeout=30,
    cache_size="50MB",
    max_retries=3,
    debug=True
)
```

## 🛠️ Troubleshooting

### Common Issues

**"Connection refused" errors:**
```bash
# Make sure server is running first
python examples/server/basic_server.py
```

**Import errors:**
```bash
# Install missing packages
pip install numpy pandas matplotlib  # for data science server
```

**Port conflicts:**
```bash
# Use different ports for multiple servers
# basic_server.py uses 8000
# data_science_server.py uses 8001
```

### Server Status Check
```bash
# Check if server is running
curl http://localhost:8000/health

# Or in Python
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

## 📚 Next Steps

1. **Start with Basic Examples**: Begin with `basic_server.py` and `basic_usage.py`
2. **Explore Streaming**: Try `streaming_demo.py` for real-time features
3. **Build Custom Servers**: Use examples as templates for your own servers
4. **Integrate with Projects**: Add PyCDN to your existing applications
5. **Contribute**: Submit your own example use cases!

## 🤝 Contributing Examples

We welcome new examples! Please follow this structure:
- Add server examples to `examples/server/`
- Add client examples to `examples/client/`
- Include clear documentation and usage instructions
- Test with multiple Python versions
- Add appropriate error handling

---

**Happy coding with PyCDN! 🚀** 