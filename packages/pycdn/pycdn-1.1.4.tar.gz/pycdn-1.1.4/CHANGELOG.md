# PyCDN Changelog

All notable changes to this project will be documented in this file.

## [1.1.4] - 2025-01-27

### 🔧 CRITICAL FIX - Chained Attribute Access
- **MAJOR FIX**: Fixed "'CDNMethodProxy' object has no attribute 'completions'" error for chained method calls
- **ROOT CAUSE**: CDNMethodProxy and CDNCallableProxy didn't support nested attribute access (e.g., `client.chat.completions.create()`)
- **SOLUTION**: Added `__getattr__` method to both proxy classes for proper attribute chaining
- **IMPACT**: Complex API patterns now work correctly:
  - OpenAI: `client.chat.completions.create()` ✅
  - Pandas: `df.plot.bar()` ✅  
  - Any nested method/attribute access ✅

### 🚀 Enhanced Method Chaining
- **NEW**: Full support for unlimited nested attribute access
- **IMPROVED**: CDNMethodProxy now supports chains like `obj.method1.method2.method3()`
- **ENHANCED**: CDNCallableProxy supports nested callable access patterns
- **TESTED**: Comprehensive testing with OpenAI's complex API structure

### 📦 What This Fixes
- OpenAI `client.chat.completions.create()` patterns
- Pandas plotting methods like `df.plot.bar()`
- Any library with nested method/attribute structures
- Complex API chaining scenarios that previously failed

## [1.1.3] - 2025-01-27

### 🔧 CRITICAL BUG FIX - Class Instantiation
- **MAJOR FIX**: Fixed "OpenAI.__init__() missing 1 required positional argument: 'self'" error
- **ROOT CAUSE**: CDNInstanceProxy was calling `ClassName.__init__` directly instead of proper class constructor
- **SOLUTION**: Changed to call class constructor properly for both classic and natural import syntax
- **IMPACT**: All class instantiation now works correctly for both syntax patterns:
  - Classic: `cdn.openai.OpenAI(api_key=...)` ✅
  - Natural: `from cdn.openai import OpenAI; OpenAI(api_key=...)` ✅

### 🚀 Enhanced Development Experience
- **NEW**: `server.py` - Simple server setup script for easy development
- **IMPROVED**: Enhanced error messages for class instantiation failures
- **ADDED**: Better debugging output and troubleshooting information
- **TESTED**: Comprehensive testing to ensure both import patterns work flawlessly

### 📦 Developer Tools
- Simplified server setup with `python server.py`
- Enhanced client examples with working class instantiation
- Better error handling and debugging capabilities
- Improved documentation for setup and troubleshooting

## [1.1.2] - 2025-01-27

### 🚀 MAJOR RELEASE - Revolutionary Hybrid Import System
- **BREAKTHROUGH**: Complete rewrite of import system with advanced `sys.meta_path` integration
- **NATURAL SYNTAX**: Full support for `from cdn.openai import OpenAI` alongside classic `cdn.openai.OpenAI()`
- **HYBRID ARCHITECTURE**: Both import styles share the same optimized backend with zero duplication
- **PRODUCTION READY**: Thread-safe, memory-efficient, and enterprise-grade implementation

### 🎯 Advanced Meta Path System
- **`HybridCDNFinder`**: Sophisticated meta path finder using `importlib.abc.MetaPathFinder`
- **`HybridCDNLoader`**: Advanced module loader with `importlib.abc.Loader` implementation
- **`HybridCDNProxy`**: Comprehensive proxy system handling modules, functions, classes, and instances
- **Smart Error Handling**: `PyCDNRemoteError` with detailed remote traceback preservation
- **Auto-Registration**: Seamless integration with Python's import machinery

### 🌟 Enhanced User Experience
- **Unified API**: `register_hybrid_cdn()`, `unregister_hybrid_cdn()`, `get_hybrid_mappings()`
- **Legacy Support**: Full backward compatibility with existing `register_cdn_client()` functions
- **Multi-CDN Management**: Support for multiple CDN connections with custom prefixes
- **Development Tools**: Enhanced debugging and introspection capabilities
- **Memory Optimized**: Zero local package footprint with intelligent proxy objects

### 📖 Comprehensive Documentation Updates
- **Complete README Rewrite**: Showcases hybrid import system capabilities
- **Advanced Examples**: 
  - `test_natural_import.py`: Comprehensive test suite for natural imports
  - Updated examples demonstrating both classic and natural syntax
- **API Documentation**: Detailed coverage of meta path system and hybrid architecture

### 🔧 Technical Improvements  
- **Performance**: Optimized proxy creation and method resolution
- **Thread Safety**: Proper locking mechanisms for concurrent operations
- **Error Resilience**: Graceful handling of import failures and network issues
- **Code Quality**: Enhanced type hints and comprehensive error messages

## [1.1.1] - 2025-01-27

### 🔥 REVOLUTIONARY FEATURE - Natural Import System
- **GAME-CHANGER**: Advanced meta path import hook system using `sys.meta_path`
- **NATURAL SYNTAX**: Now supports `from cdn.openai import OpenAI` alongside classic `cdn.openai.OpenAI()`
- **SEAMLESS INTEGRATION**: Import packages from CDN servers as if they were installed locally
- **MULTI-CDN SUPPORT**: Different prefixes for multiple CDN connections
- **DYNAMIC PREFIX MANAGEMENT**: Change import prefixes on-the-fly with `cdn.set_prefix()`
- **HYBRID USAGE**: Classic and natural import syntax work together seamlessly

### 🌟 Advanced Import Features
- **`PyCDNMetaPathFinder`**: Sophisticated import interception and resolution
- **Complete Proxy System**: 
  - `CDNModuleProxy`: Remote module representation
  - `CDNFunctionProxy`: Remote function execution
  - `CDNClassProxy`: Remote class access and instantiation
  - `CDNInstanceProxy`: Remote class instance management
  - `CDNMethodProxy`: Instance method calls with state preservation
- **`PyCDNRemoteError`**: Comprehensive error handling with remote traceback support
- **Auto-registration**: Meta path finder automatically installed on module import

### 🎯 Enhanced User Experience
- **Natural Python Workflow**: `from cdn.package import Class` feels exactly like local imports
- **Custom Prefixes**: `pycdn.pkg("url", prefix="ml")` enables `from ml.tensorflow import keras`
- **Multiple CDNs**: Connect to different servers with unique prefixes simultaneously
- **Development Mode**: Enhanced debugging and local fallback capabilities
- **CDN Management**: View, register, and clear CDN mappings dynamically

### 📖 Updated Documentation & Examples
- **Revolutionary README**: Completely rewritten to showcase natural import system
- **Advanced Examples**: 
  - `examples/quick_import_start.py`: Basic natural import usage
  - `examples/client/advanced_import_demo.py`: Comprehensive feature showcase
- **Root Examples Updated**: `client.py` and `server.py` demonstrate both classic and natural syntax
- **API Documentation**: Enhanced with meta path system details

### 🔧 Technical Improvements
- **Thread-Safe**: Proper locking for concurrent import operations
- **Memory Efficient**: Only proxy objects stored locally, zero package footprint
- **Performance Optimized**: Intelligent caching prevents redundant calls
- **Error Resilience**: Graceful handling of import failures and remote errors

## [1.1.0] - 2025-01-27

### 🔧 Fixed - Critical Cloud Deployment Issue
- **MAJOR FIX**: Enhanced auto-installation for cloud environments (Appwrite, GCP Cloud Run, AWS Lambda)
- **Multi-method Package Installation**: Added 4 fallback installation methods for restrictive cloud environments:
  1. Direct pip API (for older pip versions)
  2. Standard subprocess with `--user` flag
  3. pip._internal API (for newer pip versions) 
  4. Target installation to `/tmp` directory with path injection
- **Improved Import Resolution**: Enhanced package loading with cache invalidation and alternative path detection
- **Cloud-Compatible Server Setup**: Updated `cloud_server_setup.py` with pre-installation of common packages
- **Better Error Handling**: More descriptive error messages for debugging cloud deployment issues
- **Submodule Support**: Fixed installation of packages with submodules (e.g., `openai.ChatCompletion`)

### 🌟 Enhanced Features
- **Intelligent Path Management**: Automatically adds `/tmp` and user directories to Python path when needed
- **Installation Resilience**: Continues operation even if some packages fail to install
- **Cloud Environment Detection**: Better handling of restricted subprocess environments
- **Improved Logging**: Enhanced debug logging for troubleshooting installation issues

### 📦 Updated Dependencies
- Updated cloud deployment requirements for better compatibility

## [1.0.9] - 2025-01-27

### 🔧 Fixed - Critical Dotenv Compatibility
- **MAJOR FIX**: Removed monkey-patching of `load_dotenv()` that was interfering with normal environment variable loading
- **Perfect .env Support**: Fixed issue where `.env` files weren't loading properly, causing `OPENAI_API_KEY` to return `None`
- **Smart Environment Detection**: Enhanced `os.getenv()` monkey-patching to detect sensitive variables only when accessed
- **Client-side .env Compatibility**: Works seamlessly with user's existing `.env` files in working directory

### 🔐 Security Improvements
- **Non-Intrusive Encryption**: Encryption system no longer interferes with standard Python dotenv workflow
- **Better Token Detection**: Improved pattern matching for OpenAI (`sk-`), Anthropic (`ant-`), and HuggingFace (`hf_`) tokens
- **Deterministic Key Exchange**: Enhanced key derivation system for cloud compatibility

### 📋 Updated Documentation
- Updated examples to reflect new dotenv compatibility
- Added troubleshooting guide for environment variable issues

## [1.0.8] - 2025-01-27

### 🔐 Enhanced Security - Deterministic Key Exchange
- **FIXED**: Shared secret synchronization problem between client and server
- **NEW**: Deterministic key derivation system - no more manual secret sharing needed
- **IMPROVED**: `pycdn.enable_encryption()` now works without parameters
- **ENHANCED**: Better integration with `python-dotenv` for environment variable management

### 🔧 Dependencies Updated
- Added `cryptography>=41.0.0` for robust encryption
- Added `python-dotenv>=1.0.0` for environment variable support

### 🌟 User Experience
- **ONE-LINE ACTIVATION**: Simply call `pycdn.enable_encryption()` with no configuration
- **AUTOMATIC DETECTION**: Monkey-patched `os.getenv()` and `load_dotenv()` to track sensitive values
- **SEAMLESS WORKFLOW**: Works transparently with existing environment variable usage

## [1.0.7] - 2025-01-27

### 🔐 Major Security Enhancement - Built-in End-to-End Encryption
- **NEW**: Comprehensive built-in encryption system with `PyCDNEncryption` class
- **AUTO-DETECTION**: Smart detection of sensitive parameters (`api_key`, `token`, `secret`, etc.)
- **CLIENT-SIDE ENCRYPTION**: Automatic encryption using Fernet + PBKDF2 key derivation
- **SERVER-SIDE DECRYPTION**: Transparent decryption before function execution
- **ONE-LINE ACTIVATION**: Enable with `pycdn.enable_encryption(shared_secret="password")`

### 🔧 Enhanced Architecture
- **NEW MODULE**: `pycdn/utils/encryption.py` with full encryption capabilities
- **SEAMLESS INTEGRATION**: Works transparently with existing PyCDN workflows
- **PERFORMANCE OPTIMIZED**: Minimal overhead with efficient encryption algorithms

### 📋 Updated Examples
- Added `secure_client_example.py` demonstrating encryption usage
- Updated documentation with security best practices

## [1.0.6] - 2025-01-27

### 🚀 Enhanced Cloud Deployment & Auto-Installation
- **AUTO-INSTALLATION**: Added dynamic package installation for cloud functions
- **CLOUD SECURITY**: Created `cloud_server_setup.py` with security headers and production optimizations
- **CLOUD COMPATIBILITY**: Enhanced server for cloud run functions and serverless environments

### 🔧 Bug Fixes & Improvements
- **IMPROVED**: Better error handling for cloud environments
- **ENHANCED**: Security middleware for production deployments
- **ADDED**: Request logging and monitoring for cloud operations

## [1.0.5] - 2025-01-27

### 🔧 Critical Instance Method Fix
- **FIXED**: `RuntimeError: Remote execution failed` for instance method calls
- **ENHANCED**: `LazyAttribute.__call__` now creates proper `__instance_call__` payloads
- **IMPROVED**: Better method resolution for chained instance calls

### 🚀 Performance Improvements
- More efficient instance method execution
- Reduced network overhead for method calls

## [1.0.4] - 2025-01-27

### 🔧 Critical Server Error Response Fix
- **FIXED**: `pydantic_core.ValidationError` when server-side execution failed
- **ENHANCED**: Made `ExecuteResponse.result` field optional to handle error cases
- **IMPROVED**: Better error propagation from server to client

### 📋 Updated Models
- Enhanced response model validation
- Better error handling in response serialization

## [1.0.3] - 2025-01-27

### 🔧 Critical Chained Attribute Access Fix
- **FIXED**: `AttributeError: 'LazyMethod' object has no attribute 'completions'`
- **NEW**: `LazyAttribute` class supporting unlimited chaining
- **ENHANCED**: Perfect support for patterns like `client.chat.completions.create()`

### 🚀 Architecture Improvements
- Better lazy loading with attribute chaining
- Enhanced method resolution for complex APIs
- Improved compatibility with modern Python packages

## [1.0.2] - 2025-01-27

### 🔧 Critical Serialization Fix
- **FIXED**: `TypeError: cannot pickle '_thread.RLock' object`
- **ENHANCED**: `serialize_args()` with `_process_arg()` helper function
- **IMPROVED**: Detection and conversion of LazyInstance objects to serializable references

### 🚀 Enhanced Lazy Loading
- Better handling of complex object serialization
- Improved thread safety for concurrent operations

## [1.0.1] - 2025-01-27

### 🚀 Initial Release - Revolutionary Python Package CDN
- **CORE**: CDN-based package delivery with lazy loading
- **LAZY LOADING**: Dynamic import and execution of remote packages
- **SERVERLESS**: FastAPI-based server for package hosting
- **WEBSOCKETS**: Real-time streaming support
- **SECURITY**: Sandboxed execution environment
- **EXAMPLES**: Comprehensive examples for OpenAI, TensorFlow, PyTorch
- **CLI**: Command-line interface for server management

### 🌟 Key Features
- Netflix-like experience for Python packages
- Elimination of dependency hell
- Instant access to any Python package
- Zero local storage overhead
- Enterprise-grade security
- Cloud-native architecture

---

## Legend
- 🚀 **New Features**
- 🔧 **Bug Fixes** 
- 🔐 **Security**
- 🌟 **Enhancements**
- 📋 **Documentation**
- �� **Dependencies** 