# PyPI Publishing Guide - Azure Cost Analyzer CLI

This guide explains how to publish the Azure Cost Analyzer CLI package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Generate API tokens for both accounts:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/

3. **Required Tools**: Install build and upload tools:
   ```bash
   pip install build twine
   ```

## Publishing Process

### Step 1: Prepare the Package

1. **Update Version**: Increment version in:
   - `azure_cost_analyzer_cli/__init__.py`
   - `setup.py`
   - `pyproject.toml`

2. **Update Documentation**: Ensure README.md and CHANGELOG are current

3. **Clean Previous Builds**:
   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

### Step 2: Build the Package

```bash
python -m build
```

This creates:
- `dist/azure_cost_analyzer_cli-X.X.X.tar.gz` (source distribution)
- `dist/azure_cost_analyzer_cli-X.X.X-py3-none-any.whl` (wheel distribution)

### Step 3: Test on Test PyPI

1. **Upload to Test PyPI**:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Install from Test PyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ azure-cost-analyzer-cli
   ```

3. **Test the Installation**:
   ```bash
   azure-cost-analyzer --version
   azure-cost-analyzer --help
   ```

### Step 4: Publish to Production PyPI

1. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

2. **Verify Installation**:
   ```bash
   pip install azure-cost-analyzer-cli
   azure-cost-analyzer --version
   ```

## Configuration Files

### .pypirc Configuration

Create `~/.pypirc` for authentication:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_API_TOKEN_HERE
```

### Environment Variables

Alternatively, use environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR_API_TOKEN_HERE
```

## Version Management

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Example versions:
- `2.0.0` - Initial PyPI release
- `2.0.1` - Bug fix release
- `2.1.0` - New features
- `3.0.0` - Breaking changes

## Quality Checks

Before publishing, run quality checks:

```bash
# Check package metadata
python -m twine check dist/*

# Verify package contents
tar -tzf dist/azure_cost_analyzer_cli-*.tar.gz

# Test installation in clean environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install dist/azure_cost_analyzer_cli-*.whl
azure-cost-analyzer --help
deactivate
rm -rf test_env
```

## Automation

### GitHub Actions Workflow

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

### Manual Publishing Script

Create `scripts/publish.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Publishing Azure Cost Analyzer CLI to PyPI"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build package
echo "📦 Building package..."
python -m build

# Check package
echo "🔍 Checking package..."
python -m twine check dist/*

# Upload to Test PyPI first
echo "🧪 Uploading to Test PyPI..."
python -m twine upload --repository testpypi dist/*

read -p "Test installation successful? Upload to production PyPI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Uploading to production PyPI..."
    python -m twine upload dist/*
    echo "✅ Package published successfully!"
else
    echo "❌ Publication cancelled"
fi
```

## Troubleshooting

### Common Issues

1. **Version Already Exists**: PyPI doesn't allow re-uploading the same version
   - Solution: Increment version number

2. **Authentication Failed**: Check API tokens and .pypirc configuration
   - Solution: Regenerate tokens and update configuration

3. **Package Description Issues**: README.md formatting problems
   - Solution: Test with `python -m twine check dist/*`

4. **Missing Dependencies**: Required packages not specified correctly
   - Solution: Update `requirements.txt` and `pyproject.toml`

### Support

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/

## Post-Publication

1. **Update Repository**: Tag the release in Git
2. **Documentation**: Update installation instructions
3. **Announcement**: Notify users of the new release
4. **Monitor**: Check for issues and user feedback

---

**Note**: This package is maintained by Qanooni for internal use. Publishing to PyPI makes it available for broader enterprise deployment. 