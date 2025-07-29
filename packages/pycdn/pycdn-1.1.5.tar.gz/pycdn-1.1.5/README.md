# PyCDN - Revolutionary Package CDN with Natural Import System 🚀

**The Netflix of Python packages** - Stream packages instantly without local installation!

PyCDN revolutionizes Python package management by serving packages through CDN networks with lazy loading and **natural import syntax**. Say goodbye to dependency hell and `pip install` delays!

## 🌟 Revolutionary Import System

PyCDN now supports **natural Python import syntax** using an advanced meta path import hook system. This means you can import packages directly from CDN servers as if they were installed locally!

### Classic Usage (Still Works)
```python
import pycdn

# Connect to CDN server
cdn = pycdn.pkg("http://localhost:8000")

# Use packages via attribute access
result = cdn.math.sqrt(16)  # Returns 4.0
data = cdn.numpy.array([1, 2, 3, 4, 5])
model = cdn.sklearn.LinearRegression()
```

### 🎯 NEW: Natural Import Syntax
```python
import pycdn

# Connect and register CDN
cdn = pycdn.pkg("http://localhost:8000")  # Registers 'cdn' prefix

# Now use natural Python imports!
from cdn.openai import OpenAI
from cdn.numpy import array, mean
from cdn.pandas import DataFrame
from cdn.sklearn.ensemble import RandomForestClassifier

# Use exactly like local packages
client = OpenAI(api_key="your-key")
data = array([1, 2, 3, 4, 5])
avg = mean(data)
df = DataFrame({"col1": [1, 2, 3]})
model = RandomForestClassifier()
```

### 🔧 Custom Import Prefixes
```python
# Use custom prefixes for different CDN servers
ml_cdn = pycdn.pkg("http://ml-cdn:8000", prefix="ml")
data_cdn = pycdn.pkg("http://data-cdn:8000", prefix="data")

# Import from different CDNs
from ml.tensorflow import keras
from ml.pytorch import nn
from data.pandas import DataFrame
from data.dask import dataframe as dd
```

### 🏢 Multiple CDN Support
```python
# Connect to multiple CDN environments
prod = pycdn.pkg("http://prod-cdn:8000", prefix="prod")
dev = pycdn.pkg("http://dev-cdn:8000", prefix="dev")
test = pycdn.pkg("http://test-cdn:8000", prefix="test")

# Import from specific environments
from prod.stable_package import ProductionClass
from dev.beta_package import ExperimentalFeature
from test.mock_package import TestDouble
```

## 🎯 Key Features

- **🔥 Natural Import Syntax**: Use `from cdn.package import Class` - feels exactly like local imports
- **⚡ Instant Access**: No `pip install` required - packages execute remotely
- **🌍 Global CDN**: Packages served from edge locations worldwide
- **🔒 Zero Dependencies**: No local installation or dependency conflicts
- **💾 Smart Caching**: Intelligent caching with hybrid in-memory + disk storage
- **🛡️ Security**: Sandboxed execution with runtime security scanning
- **📊 Analytics**: Usage tracking and performance monitoring
- **🔄 Multi-CDN**: Connect to multiple CDN servers simultaneously
- **🧰 Development Mode**: Local fallback and enhanced debugging

## 🚀 Installation

```bash
pip install pycdn
```

## 📖 Quick Start

### 1. Basic Usage
```python
import pycdn

# Connect to CDN
cdn = pycdn.pkg("http://localhost:8000")

# Classic usage
result = cdn.math.sqrt(16)
print(result)  # 4.0

# Natural imports (NEW!)
from cdn.math import sqrt, pow
print(sqrt(25))    # 5.0
print(pow(2, 3))   # 8.0
```

### 2. Working with Classes
```python
import pycdn

cdn = pycdn.pkg("http://localhost:8000")

# Import and use classes naturally
from cdn.openai import OpenAI
from cdn.sklearn.ensemble import RandomForestClassifier

# Create instances and call methods
client = OpenAI(api_key="your-key")
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

### 3. Data Science Workflow
```python
import pycdn

# Connect to data science CDN
ds_cdn = pycdn.pkg("http://ds-cdn:8000", prefix="ds")

# Natural imports for entire data pipeline
from ds.pandas import DataFrame, read_csv
from ds.numpy import array, mean, std
from ds.matplotlib.pyplot as plt
from ds.sklearn.model_selection import train_test_split
from ds.sklearn.ensemble import RandomForestRegressor
from ds.sklearn.metrics import mean_squared_error

# Use exactly like local packages
df = read_csv("data.csv")
X = df[["feature1", "feature2"]]
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)

predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f"MSE: {mse}")
```

## 🛠️ Advanced Features

### Dynamic Prefix Management
```python
cdn = pycdn.pkg("http://localhost:8000", prefix="initial")

# Change prefix dynamically
cdn.set_prefix("dynamic")

# Enable specific package imports
cdn.enable_imports(["tensorflow", "pytorch", "scikit-learn"])

# Now these work:
from dynamic.tensorflow import keras
from dynamic.pytorch import nn
```

### Error Handling
```python
from pycdn import PyCDNRemoteError

try:
    from cdn.nonexistent import something
except PyCDNRemoteError as e:
    print(f"CDN Error: {e.message}")
    print(f"Package: {e.package_name}")
    if e.remote_traceback:
        print(f"Remote traceback: {e.remote_traceback}")
```

### Development Mode
```python
# Configure for development
pycdn.configure(debug=True, timeout=60)

cdn = pycdn.pkg("http://localhost:8000", prefix="dev")
# Enables local fallback, enhanced debugging, mock mode
```

### CDN Management
```python
# View active CDN mappings
mappings = pycdn.get_cdn_mappings()
print(mappings)  # {'cdn': 'http://localhost:8000', 'ml': 'http://ml-cdn:8000'}

# Clear all mappings
pycdn.clear_cdn_mappings()

# Register/unregister specific prefixes
pycdn.register_cdn_client("custom", cdn_client)
pycdn.unregister_cdn_client("custom")
```

## 🏗️ Server Setup

Deploy packages to your CDN server:

```python
from pycdn.server import CDNServer

# Create CDN server
server = CDNServer(port=8000)

# Deploy packages
server.deploy_package("math", version="1.0.0")
server.deploy_package("numpy", version="1.24.0")
server.deploy_package("openai", version="1.0.0")

# Start server
server.start()
```

## 🌐 Meta Path Import System

PyCDN uses Python's `sys.meta_path` to intercept imports and resolve them from CDN servers:

```python
import sys
import pycdn

# When you create a CDN connection
cdn = pycdn.pkg("http://localhost:8000", prefix="cdn")

# PyCDN automatically:
# 1. Registers a MetaPathFinder in sys.meta_path
# 2. Maps the 'cdn' prefix to your CDN client
# 3. Intercepts imports starting with 'cdn.'
# 4. Creates proxy objects that execute remotely
# 5. Handles classes, functions, modules transparently

# All of this happens automatically!
from cdn.package import Class  # Intercepted and resolved
```

## 🔧 Configuration

```python
# Global configuration
pycdn.configure(
    debug=True,
    timeout=30,
    cache_size="100MB",
    max_retries=3
)

# Per-connection configuration
cdn = pycdn.pkg(
    "http://localhost:8000",
    prefix="cdn",
    timeout=60,
    api_key="your-api-key",
    region="us-east-1",
    cache_size="500MB",
    max_retries=5,
    debug=True
)
```

## 📊 Performance

- **🚀 First call**: ~50-100ms (network + execution)
- **⚡ Cached calls**: ~1-5ms (local cache hit)
- **💾 Memory usage**: Minimal (only proxy objects stored locally)
- **🌍 Global reach**: CDN edge servers reduce latency worldwide
- **📈 Scalability**: Automatic scaling based on demand

## 🛡️ Security

- **🔒 Sandboxed execution**: Each package runs in isolated environment
- **🛡️ Runtime scanning**: Real-time security vulnerability detection
- **🚫 Package allowlists**: Control which packages can be imported
- **🔐 API authentication**: Secure CDN access with API keys
- **📝 Audit logs**: Complete execution history and monitoring

## 🧪 Examples

Check out our comprehensive examples:

- [`examples/quick_import_start.py`](examples/quick_import_start.py) - Basic import system usage
- [`examples/client/advanced_import_demo.py`](examples/client/advanced_import_demo.py) - Advanced features showcase
- [`examples/client/basic_usage.py`](examples/client/basic_usage.py) - Classic PyCDN usage
- [`examples/server/`](examples/server/) - Server deployment examples

## 🤝 Contributing

We welcome contributions! Check out our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

Apache-2.0 License - see [LICENSE](LICENSE) for details.

## 🌟 Why PyCDN?

Traditional package management is broken:
- ❌ Long installation times
- ❌ Dependency conflicts
- ❌ Storage space waste
- ❌ Environment inconsistencies
- ❌ Version management complexity

PyCDN fixes all of this:
- ✅ **Instant access** - no installation needed
- ✅ **Zero conflicts** - packages run remotely
- ✅ **Minimal storage** - only proxy objects locally
- ✅ **Consistent environments** - CDN guarantees consistency
- ✅ **Automatic updates** - always use latest versions
- ✅ **Natural syntax** - import exactly like local packages

---

**PyCDN: The Netflix of Python packages** 🎬  
*Stream packages instantly, anywhere, anytime!*