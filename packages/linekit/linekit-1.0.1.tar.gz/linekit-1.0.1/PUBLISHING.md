# 🚀 Publishing LINE API Integration Library

This guide explains how to publish the LINE API Integration Library to PyPI using the automated publish script.

## Prerequisites

Before publishing, ensure you have:

1. **PyPI Account**: Create accounts on both [PyPI](https://pypi.org/account/register/) and [Test PyPI](https://test.pypi.org/account/register/)
2. **API Tokens**: Generate API tokens for uploading packages:
   - [PyPI API Token](https://pypi.org/manage/account/token/)
   - [Test PyPI API Token](https://test.pypi.org/manage/account/token/)
3. **Git Repository**: Ensure all changes are committed and you're on a release branch

## Using the Publish Script

The `publish.sh` script automates the entire publishing process with built-in quality checks.

### 1. Prepare for Release

```bash
# Create a release branch
git checkout -b release/v1.0.0

# Update version numbers if needed
# - pyproject.toml: version = "1.0.0"
# - line_api/__init__.py: __version__ = "1.0.0"
# - CHANGELOG.md: Add release notes
```

### 2. Run the Publish Script

```bash
# Make sure you're in the project root
cd /path/to/line-api

# Run the publish script
./publish.sh
```

### 3. Script Workflow

The script will automatically:

1. **Environment Setup**
   - Check prerequisites (Python, UV)
   - Create/activate virtual environment
   - Install dependencies and build tools

2. **Quality Checks**
   - Run ruff linting (with option to continue if minor issues)
   - Run mypy type checking (with option to continue if issues)
   - Run comprehensive pytest test suite

3. **Build Package**
   - Clean previous builds
   - Build source distribution and wheel
   - Validate package contents with twine

4. **Publishing Options**
   - **Option 1**: Upload to Test PyPI (recommended for first time)
   - **Option 2**: Upload to PyPI (production release)
   - **Option 3**: Create GitHub release tag only
   - **Option 4**: Exit without publishing

## Publishing Workflow

### First Time Release

1. **Test PyPI First** (Option 1)
   ```bash
   ./publish.sh
   # Choose option 1: Upload to Test PyPI
   ```

2. **Verify Installation**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ line-api-integration
   ```

3. **Test the Package**
   ```python
   import line_api
   print(line_api.__version__)
   ```

### Production Release

1. **Publish to PyPI** (Option 2)
   ```bash
   ./publish.sh
   # Choose option 2: Upload to PyPI
   ```

2. **Create GitHub Release**
   - The script will offer to create a git tag
   - Push the tag: `git push origin v1.0.0`
   - Create GitHub release at: https://github.com/your-username/line-api-integration/releases/new

## Version Management

### Semantic Versioning

- **Major (1.0.0)**: Breaking changes
- **Minor (1.1.0)**: New features, backward compatible
- **Patch (1.0.1)**: Bug fixes, backward compatible

### Update Process

1. Update version in `pyproject.toml`
2. Update version in `line_api/__init__.py`
3. Update `CHANGELOG.md` with release notes
4. Commit changes
5. Run publish script

## Troubleshooting

### Common Issues

1. **Linting Errors**: The script allows you to continue with minor linting issues
2. **Test Failures**: Fix failing tests before publishing
3. **Build Errors**: Check `pyproject.toml` configuration
4. **Upload Errors**: Verify API tokens and network connection

### Quality Checks

The script enforces these quality standards:
- Code linting with ruff
- Type checking with mypy
- Test coverage with pytest
- Package validation with twine

### API Token Setup

1. **Create ~/.pypirc** (optional, for convenience):
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

2. **Or enter tokens when prompted** by the script

## Release Checklist

- [ ] All tests passing
- [ ] Version updated in all files
- [ ] CHANGELOG.md updated
- [ ] All changes committed
- [ ] On release branch
- [ ] Test PyPI upload successful
- [ ] Package installation verified
- [ ] PyPI upload successful
- [ ] GitHub release created
- [ ] Documentation updated

## Support

For issues with the publish script or release process:
1. Check the script output for specific error messages
2. Verify all prerequisites are met
3. Ensure API tokens are valid
4. Review the troubleshooting section above

The publish script provides detailed output and error messages to help diagnose any issues during the release process.
