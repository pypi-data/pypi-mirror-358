# PyCDN Publishing Guide

This guide will walk you through publishing PyCDN to PyPI and other distribution channels.

## Prerequisites

Before publishing, ensure you have:

1. **Python packaging tools installed:**
   ```bash
   pip install --upgrade pip setuptools wheel twine build
   ```

2. **PyPI account setup:**
   - Create account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
   - Create account at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/) for testing
   - Set up API tokens for secure authentication

3. **Project validation:**
   ```bash
   # Ensure all tests pass
   python -m pytest tests/
   
   # Verify package structure
   python setup.py check --strict --metadata
   ```

## Step 1: Prepare the Package

### 1.1 Update Version Numbers

Update version in multiple files:

**`setup.py`:**
```python
version="1.0.0",  # Update this
```

**`pyproject.toml`:**
```toml
version = "1.0.0"  # Update this
```

**`pycdn/__init__.py`:**
```python
__version__ = "1.0.0"  # Update this
```

### 1.2 Finalize Documentation

Ensure these files are complete and accurate:
- `README.md` - Main project description
- `README_MVP.md` - MVP documentation
- `docs/quickstart.md` - User guide
- `CHANGELOG.md` - Version history (create if needed)
- `LICENSE` - Apache 2.0 license

### 1.3 Clean Build Environment

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info/

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Step 2: Build the Package

### 2.1 Build Distribution Files

```bash
# Build source and wheel distributions
python -m build

# This creates:
# - dist/pycdn-1.0.0.tar.gz (source distribution)
# - dist/pycdn-1.0.0-py3-none-any.whl (wheel distribution)
```

### 2.2 Verify Build

```bash
# Check the built package
python -m twine check dist/*

# Install and test locally
pip install dist/pycdn-1.0.0-py3-none-any.whl

# Test basic functionality
python -c "import pycdn; print(pycdn.__version__)"
```

## Step 3: Test on Test PyPI

### 3.1 Upload to Test PyPI

```bash
# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# You'll be prompted for username and password
# Username: __token__
# Password: your-test-pypi-api-token
```

### 3.2 Test Installation from Test PyPI

```bash
# Create fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pycdn

# Test the installation
python examples/basic_usage.py
```

## Step 4: Publish to Production PyPI

### 4.1 Upload to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*

# Username: __token__
# Password: your-pypi-api-token
```

### 4.2 Verify Publication

```bash
# Check the package page
# https://pypi.org/project/pycdn/

# Test installation from PyPI
pip install pycdn

# Verify installation
python -c "import pycdn; print('PyCDN installed successfully!')"
```

## Step 5: Post-Publication Tasks

### 5.1 Tag the Release

```bash
# Create and push git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 5.2 Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Choose the tag you just created
4. Add release notes describing new features and changes
5. Attach the distribution files from `dist/`

### 5.3 Update Documentation

```bash
# Update package documentation
# Consider using Sphinx for comprehensive docs
pip install sphinx sphinx-rtd-theme

# Generate documentation
sphinx-quickstart docs/
# Edit docs/conf.py and add your modules
# Build docs: sphinx-build -b html docs/ docs/_build/
```

## Automation with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
        
    - name: Build package
      run: python -m build
      
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

## Security Best Practices

### 5.1 Use API Tokens

Never use username/password. Always use API tokens:

1. Go to PyPI Account Settings
2. Create API token with appropriate scope
3. Store as GitHub secret for automation

### 5.2 Verify Package Integrity

```bash
# Always verify what you're uploading
python -m twine check dist/*

# Check package contents
tar -tzf dist/pycdn-1.0.0.tar.gz
unzip -l dist/pycdn-1.0.0-py3-none-any.whl
```

## Maintenance and Updates

### 6.1 Version Management

Follow semantic versioning (semver.org):
- `MAJOR.MINOR.PATCH`
- MAJOR: incompatible API changes
- MINOR: new functionality, backwards compatible
- PATCH: backwards compatible bug fixes

### 6.2 Regular Updates

```bash
# For patch releases
git checkout main
git pull origin main
# Update version numbers
python -m build
python -m twine upload dist/*

# For feature releases
git checkout -b feature/new-feature
# Develop new features
# Update version numbers
# Create pull request
# After merge, follow publishing steps
```

## Troubleshooting

### Common Issues

1. **"File already exists" error:**
   ```bash
   # You can't overwrite existing versions
   # Increment version number and rebuild
   ```

2. **Import errors after installation:**
   ```bash
   # Check dependencies in setup.py
   # Ensure all required packages are listed
   ```

3. **Permission errors:**
   ```bash
   # Check API token permissions
   # Ensure token has upload permissions
   ```

### Testing Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass  
- [ ] Package builds without errors
- [ ] Installation from wheel works
- [ ] Basic functionality verified
- [ ] Documentation is complete
- [ ] Version numbers updated
- [ ] License file included

## Distribution Channels

Beyond PyPI, consider:

1. **Conda-forge** (for Anaconda users)
2. **GitHub Packages** (for enterprise)
3. **Docker Hub** (containerized version)
4. **Linux package managers** (apt, yum, etc.)

## Success Metrics

Track your package success:
- Download statistics on PyPI
- GitHub stars and forks
- Community feedback and issues
- Usage in other projects

---

**🎉 Congratulations! Your PyCDN package is now published and available worldwide!**

Users can now install it with:
```bash
pip install pycdn
```

And start using the revolutionary CDN-based package delivery system!