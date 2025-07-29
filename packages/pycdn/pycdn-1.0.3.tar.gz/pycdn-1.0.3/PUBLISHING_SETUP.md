# 🚀 PyCDN Publishing Setup Guide

## 🏗️ **Prerequisites for Publishing**

### 1. PyPI Account Setup
```bash
# 1. Create accounts at:
# - PyPI: https://pypi.org/account/register/
# - Test PyPI: https://test.pypi.org/account/register/

# 2. Generate API tokens:
# - PyPI: https://pypi.org/manage/account/token/
# - Test PyPI: https://test.pypi.org/manage/account/token/
```

### 2. GitHub Repository Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:
- `PYPI_API_TOKEN` - Your PyPI API token (starts with `pypi-`)
- `TEST_PYPI_API_TOKEN` - Your Test PyPI API token

## 🔄 **Automated Publishing Workflow**

### Publishing via GitHub Releases (Recommended)
```bash
# 1. Commit all changes
git add .
git commit -m "Release v1.0.1 with new examples structure"

# 2. Create and push a version tag
git tag v1.0.2
git push origin main --tags

# 3. Create a GitHub Release
# Go to GitHub → Releases → "Create a new release"
# - Tag: v1.0.2
# - Title: "PyCDN v1.0.2 - Fixed LazyInstance Serialization Bug"
# - Description: Your release notes
# - Click "Publish release"

# ✅ This automatically triggers the GitHub Actions workflow!
```

### Manual Publishing via GitHub Actions
```bash
# Alternative: Trigger manual workflow
# Go to GitHub → Actions → "Publish to PyPI" → "Run workflow"
# This publishes to Test PyPI for testing
```

## 📦 **Manual Publishing (Local)**

### Test PyPI (for testing)
```bash
# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/pycdn-1.0.1*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ pycdn==1.0.1
```

### Production PyPI
```bash
# Upload to production PyPI
python -m twine upload dist/pycdn-1.0.1*

# Test installation from PyPI
pip install pycdn==1.0.1
```

## 🎯 **Release Workflow**

### Complete Release Process
```bash
# 1. Update version numbers (already done for v1.0.2)
# 2. Build and test locally
python -m build
python -m twine check dist/*

# 3. Commit and tag
git add .
git commit -m "Release v1.0.2 - Fixed LazyInstance serialization bug"
git tag v1.0.2
git push origin main --tags

# 4. Create GitHub Release
# This triggers automated publishing via GitHub Actions

# 5. Verify installation
pip install pycdn==1.0.2
python -c "import pycdn; print(f'✅ PyCDN {pycdn.__version__} installed')"
```

## 🔧 **GitHub Actions Features**

### Automated Workflows
- **Tests**: Run on every push/PR across Python 3.8-3.12
- **Build**: Creates distribution packages automatically  
- **Publish**: Uploads to PyPI on releases and version tags
- **Test Publish**: Manual trigger for Test PyPI uploads

### Publishing Triggers
1. **GitHub Releases** → Automatic PyPI publishing
2. **Version Tags** (v*) → Automatic PyPI publishing  
3. **Manual Trigger** → Test PyPI publishing

## 📊 **Current Package Status**

### Version 1.0.2 Features
✅ **Core Features:**
- CDN-based package execution
- Lazy loading with import hooks
- WebSocket streaming support
- Client-server architecture

✅ **Examples Structure:**
- `examples/server/` - Server setup examples
- `examples/client/` - Client usage examples  
- Comprehensive documentation

✅ **Distribution:**
- Built and validated packages ready
- GitHub Actions workflows configured
- MANIFEST.in includes all files

### Files in Distribution
```
pycdn-1.0.1/
├── pycdn/                  # Core package
├── examples/               # Example scripts
├── docs/                   # Documentation
├── tests/                  # Test files
├── README.md               # Project documentation
├── EXAMPLES_GUIDE.md       # Quick start guide
└── requirements.txt        # Dependencies
```

## 🚀 **Next Steps**

1. **Set up GitHub secrets** (PYPI_API_TOKEN)
2. **Create GitHub release** for v1.0.1
3. **Verify automated publishing** works
4. **Test installation** from PyPI
5. **Update documentation** with installation instructions

## 🎉 **Ready to Publish!**

Your PyCDN v1.0.2 is ready for release with:
- ✅ Updated version numbers
- ✅ GitHub Actions workflows 
- ✅ Built and validated packages
- ✅ Comprehensive examples
- ✅ Full documentation

Just create a GitHub release to trigger automatic publishing! 🚀 