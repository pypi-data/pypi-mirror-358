# PyCDN Examples Guide

## 🎯 Quick Start (2-Step Process)

### Step 1: Start a Server
```bash
# Choose one server to start:
python examples/server/basic_server.py          # ← Recommended for beginners
python examples/server/data_science_server.py   # For data science packages
python examples/server/advanced_server.py       # Advanced features
```

### Step 2: Run Client Examples
```bash
# In a NEW terminal, run any client example:
python examples/client/basic_usage.py           # ← Start here!
python examples/client/client_example.py        # Comprehensive demo
python examples/client/streaming_demo.py        # Real-time streaming
python examples/client/openai_example.py        # AI integration
```

## 📁 New Structure

The examples are now organized into **server** and **client** folders for clarity:

```
examples/
├── server/                    # 🖥️  Server Setup Examples
│   ├── basic_server.py       #     Basic server (18 packages)
│   ├── data_science_server.py#     Data science focused
│   └── advanced_server.py    #     Advanced deployment features
├── client/                    # 📱 Client Usage Examples  
│   ├── basic_usage.py        #     Perfect for beginners
│   ├── client_example.py     #     Comprehensive client demo
│   ├── streaming_demo.py     #     Real-time streaming features
│   └── openai_example.py     #     OpenAI integration
└── README.md                  # 📖 Detailed documentation
```

## 🚀 What Each Example Does

### 🖥️ Server Examples

| Example | Port | Packages | Best For |
|---------|------|----------|----------|
| `basic_server.py` | 8000 | 18 common packages | **Beginners** |
| `data_science_server.py` | 8001 | Scientific computing | **Data Science** |
| `advanced_server.py` | 8000 | Deployment features | **Advanced Users** |

### 📱 Client Examples

| Example | Features | Best For |
|---------|----------|----------|
| `basic_usage.py` | 3 usage patterns | **Learning PyCDN** |
| `client_example.py` | Full API demo | **Understanding capabilities** |
| `streaming_demo.py` | Real-time streaming | **Interactive applications** |
| `openai_example.py` | AI integration | **External package usage** |

## ✅ Verified Working Examples

All examples have been tested and work with the new structure:

- ✅ **Server startup**: All server examples start correctly
- ✅ **Client connection**: All client examples connect to servers  
- ✅ **Package execution**: Math, JSON, OS, time operations work
- ✅ **Import paths**: All import paths fixed for new structure
- ✅ **Error handling**: Proper error messages and guidance
- ✅ **CORS enabled**: Web client support
- ✅ **Import hooks**: Advanced import functionality

## 🔧 Configuration Examples

### Basic Server Configuration
```python
# examples/server/basic_server.py
server = CDNServer(
    host="localhost",
    port=8000,
    debug=True,
    allowed_packages=["math", "json", "time", ...]  # 18 packages
)
```

### Client Connection
```python  
# examples/client/basic_usage.py
import pycdn

# Quick access
cdn = pycdn.pkg("http://localhost:8000")
result = cdn.math.sqrt(16)  # Returns 4.0

# Or full client
client = pycdn.connect("http://localhost:8000")
packages = client.list_packages()
```

## 🛠️ Troubleshooting

### "Connection refused" errors
```bash
# ✅ Solution: Start server first
python examples/server/basic_server.py
```

### "Import errors" 
```bash
# ✅ Solution: All import paths are fixed
# Examples work from project root directory
```

### Port conflicts
```bash
# ✅ Solution: Different servers use different ports
# basic_server.py → port 8000
# data_science_server.py → port 8001  
```

## 🎯 Recommended Learning Path

1. **Start Here**: `python examples/server/basic_server.py`
2. **Then Try**: `python examples/client/basic_usage.py`
3. **Next**: `python examples/client/client_example.py`
4. **Advanced**: `python examples/client/streaming_demo.py`
5. **Real-world**: `python examples/client/openai_example.py`

## 💡 Key Benefits of New Structure

- **Clear Separation**: Server setup vs client usage
- **Easy to Follow**: Step-by-step workflow
- **No Confusion**: Always know which terminal for what
- **Beginner Friendly**: Clear starting point
- **Scalable**: Easy to add more examples

---

**🚀 Ready to start? Run the Quick Start commands above!** 