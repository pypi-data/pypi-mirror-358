# PyCDN Changelog

## [1.0.5] - 2025-01-27

### 🐛 Bug Fixes
- **Fixed Instance Method Calls**: Resolved `'openai' has no attribute 'OpenAI.chat.completions.create'` error when calling methods on remote class instances
- **Enhanced LazyInstance Support**: Implemented proper handling of chained method calls on class instances (e.g., `client.chat.completions.create()`)
- **Added Instance Call Handler**: Server now properly handles instance creation and method execution in a single remote call
- **Improved OpenAI Compatibility**: Fixed the specific pattern `client = cdn.openai.OpenAI(api_key=api_key); response = client.chat.completions.create(...)`

### 🔧 Technical Changes
- Modified `LazyAttribute.__call__` to create special `__instance_call__` payloads for instance method calls
- Added `_execute_instance_method` handler in server runtime to process instance creation + method calls
- Enhanced server to distinguish between module function calls and instance method calls
- Maintained backward compatibility for existing function calls

### ✅ Fixed Use Cases
- OpenAI client instantiation and method calls now work correctly
- Complex API patterns with chained method calls (e.g., `client.chat.completions.create()`)
- Any class-based package APIs that require instance creation followed by method calls
- Third-party package integration with instance-based APIs

## [1.0.4] - 2025-01-27

### 🐛 Bug Fixes
- **Fixed Server Error Response Handling**: Resolved `pydantic_core._pydantic_core.ValidationError: Field required [type=missing, input_value={'success': False...` error that occurred when server-side function execution failed
- **Updated ExecuteResponse Model**: Made `result` field optional in `ExecuteResponse` model to properly handle error responses that don't include result data
- **Improved Error Handling**: Server now properly handles and serializes errors without causing Pydantic validation failures

### 🔧 Technical Changes
- Modified `ExecuteResponse.result` field from required `str` to optional `Optional[str] = None`
- Enhanced server error response compatibility with existing client-side error handling
- Maintained backward compatibility for successful responses

### ✅ Fixed Use Cases
- Server no longer crashes when function execution fails
- Proper error messages are now sent to clients instead of 500 Internal Server Errors
- Complex package operations that may fail are now handled gracefully
- OpenAI and other third-party package errors are properly propagated

## [1.0.3] - 2025-01-27

### 🐛 Bug Fixes
- **Fixed Chained Attribute Access**: Resolved `AttributeError: 'LazyMethod' object has no attribute 'completions'` error that occurred when accessing nested attributes like `client.chat.completions.create()`
- **Enhanced LazyAttribute Class**: Created new `LazyAttribute` class that supports both method calls and further attribute access for chained operations
- **Updated LazyFunction**: Added `__getattr__` support to `LazyFunction` for chained attribute access on function results
- **Backward Compatibility**: Maintained `LazyMethod` as a subclass of `LazyAttribute` for existing code compatibility

### 🔧 Technical Changes
- Added `LazyAttribute` class with full chained attribute access support
- Updated `LazyInstance.__getattr__()` to return `LazyAttribute` instead of `LazyMethod`
- Enhanced `LazyFunction` with `__getattr__` method for nested attribute access
- Improved attribute path handling for complex object hierarchies

### ✅ Fixed Use Cases
- `client.chat.completions.create()` - now works perfectly
- `package.module.submodule.function()` - chained module access
- `instance.property.method()` - nested property access
- Complex API patterns like OpenAI, TensorFlow, etc.

## [1.0.2] - 2025-01-27

### 🐛 Bug Fixes
- **Fixed LazyInstance Serialization Error**: Resolved `TypeError: cannot pickle '_thread.RLock' object` and `TypeError: Object of type LazyInstance is not JSON serializable` errors that occurred when creating nested LazyInstance objects
- **Improved Argument Serialization**: Enhanced `serialize_args()` and `deserialize_args()` functions to properly handle LazyInstance objects by converting them to serializable references
- **Updated LazyMethod Execution**: Modified LazyMethod to use structured request data instead of trying to serialize LazyInstance objects directly

### 🔧 Technical Changes
- Added `_process_arg()` helper function in `serialize_args()` to recursively handle LazyInstance objects
- Added `_reconstruct_arg()` helper function in `deserialize_args()` to properly reconstruct LazyInstance references
- Simplified `LazyInstance._initialize_remote_instance()` to avoid unnecessary serialization during instance creation
- Updated `LazyMethod.__call__()` to use structured request format for better instance method handling

### ✅ Verified Fixes
- LazyInstance objects can now be serialized without errors
- Nested LazyInstance objects are properly handled
- Complex object graphs with multiple LazyInstance references work correctly
- No breaking changes to existing API

## [1.0.1] - 2025-01-26

### 🎉 Features
- **Enhanced Examples Structure**: Reorganized examples into clear `server/` and `client/` directories
- **Comprehensive Documentation**: Added detailed guides and examples for both beginners and advanced users
- **GitHub Actions Setup**: Complete CI/CD workflows for automated testing and publishing

### 📁 New Examples
- `examples/server/basic_server.py` - Simple server with 18 common packages
- `examples/server/data_science_server.py` - Scientific computing focused server
- `examples/server/advanced_server.py` - Advanced deployment features
- `examples/client/basic_usage.py` - Perfect introduction for new users
- `examples/client/client_example.py` - Comprehensive client demonstration
- `examples/client/streaming_demo.py` - Real-time output streaming
- `examples/client/openai_example.py` - AI integration example

### 📚 Documentation
- `examples/README.md` - 250+ lines of comprehensive documentation
- `EXAMPLES_GUIDE.md` - Quick reference guide
- `PUBLISHING_SETUP.md` - Complete publishing workflow

### 🤖 Automation
- GitHub Actions for testing across Python 3.8-3.12
- Automated PyPI publishing on releases
- Package validation and build verification

## [1.0.0] - 2025-01-26

### 🚀 Initial Release
- **Core CDN Client**: Revolutionary package delivery system
- **Lazy Loading**: Import hooks and on-demand package loading
- **Server Framework**: FastAPI-based package serving infrastructure
- **WebSocket Streaming**: Real-time output and progress tracking
- **Multi-Package Support**: Handle multiple packages simultaneously

### 🎯 Key Features
- CDN-based package execution without local installation
- Transparent import system that works like regular Python imports
- Intelligent caching and performance optimization
- Cross-platform compatibility (Windows, macOS, Linux)
- Enterprise-ready with proper error handling and logging

### 🔧 Technical Architecture
- Client-server architecture with RESTful API
- CloudPickle serialization for complex objects
- Import hook system for seamless package loading
- Configurable CDN endpoints and failover support
- Comprehensive test suite and examples 