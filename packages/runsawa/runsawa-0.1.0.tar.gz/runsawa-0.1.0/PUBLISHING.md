# Publishing to PyPI

This guide explains how to build and publish the `runsawa` package to PyPI.

## Prerequisites

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Create PyPI Accounts

- **Test PyPI**: https://test.pypi.org/account/register/
- **PyPI**: https://pypi.org/account/register/

### 3. Configure Authentication

#### Option A: API Tokens (Recommended)

1. Go to your PyPI account settings
2. Generate an API token
3. Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

#### Option B: Username/Password

You'll be prompted for credentials during upload.

## Building and Publishing

### Method 1: Using the Helper Script

```bash
# Build only
python build_and_upload.py --build

# Upload to Test PyPI (for testing)
python build_and_upload.py --test

# Upload to PyPI (production)
python build_and_upload.py --upload

# Clean build artifacts
python build_and_upload.py --clean
```

### Method 2: Manual Commands

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Upload to Test PyPI (for testing)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

## Testing Your Package

### Test PyPI Installation

```bash
# Install from Test PyPI
pip install -i https://test.pypi.org/simple/ sawa

# Test the installation
python -c "from sawa import sawa; print('Import successful!')"
```

### PyPI Installation

```bash
# Install from PyPI
pip install sawa

# Test the installation
python -c "from sawa import sawa; print('Import successful!')"
```

## Version Management

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Increment as needed
   ```

2. Follow [Semantic Versioning](https://semver.org/):
   - `MAJOR.MINOR.PATCH`
   - `MAJOR`: Breaking changes
   - `MINOR`: New features (backward compatible)
   - `PATCH`: Bug fixes (backward compatible)

## Pre-Publication Checklist

- [ ] All tests pass: `python -m pytest tests/`
- [ ] Version number updated in `pyproject.toml`
- [ ] README.md is up to date
- [ ] CHANGELOG updated (if you have one)
- [ ] License file exists
- [ ] Package builds successfully: `python -m build`
- [ ] Test installation from Test PyPI works
- [ ] All required files included in `MANIFEST.in`

## Troubleshooting

### Common Issues

1. **Module not found after installation**
   - Check `[tool.hatchling.build.targets.wheel]` in `pyproject.toml`
   - Ensure `packages = ["sawa"]` is correct

2. **Upload rejected**
   - Version already exists on PyPI (increment version)
   - Check package name availability

3. **Build fails**
   - Check for syntax errors in `pyproject.toml`
   - Ensure all dependencies are specified

4. **Import errors**
   - Check `__init__.py` files exist
   - Verify package structure

### Getting Help

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)

## Example Workflow

```bash
# 1. Update version and test
vim pyproject.toml  # Update version
python -m pytest tests/

# 2. Test on Test PyPI
python build_and_upload.py --test
pip install -i https://test.pypi.org/simple/ sawa
python example.py  # Test it works

# 3. Publish to PyPI
python build_and_upload.py --upload

# 4. Verify
pip install sawa
python example.py  # Final test
``` 