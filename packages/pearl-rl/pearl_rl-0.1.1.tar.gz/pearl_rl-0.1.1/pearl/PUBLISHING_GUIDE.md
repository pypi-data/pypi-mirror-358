# Publishing Pearl RL to PyPI

This guide will help you publish your Pearl RL library to PyPI so it can be installed via `pip install pearl-rl`.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI

## Before Publishing

### 1. Update Package Information

Edit the following files and replace placeholder information:

- `setup.py`: Update `author`, `author_email`, and `url`
- `pyproject.toml`: Update author information and URLs
- `README.md`: Update GitHub URLs and documentation links
- `__init__.py`: Update author information

### 2. Test Your Package Locally

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
python -m twine check dist/*

# Install locally to test
pip install dist/*.whl
```

### 3. Test Installation

Create a new virtual environment and test the installation:

```bash
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install pearl-rl
python -c "import pearl; print('Installation successful!')"
```

## Publishing Process

### Step 1: Test on TestPyPI

First, publish to TestPyPI to ensure everything works:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pearl-rl
```

### Step 2: Publish to PyPI

Once you're satisfied with the TestPyPI version:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Using the Automated Script

You can use the provided `build_and_publish.py` script:

```bash
python build_and_publish.py
```

This script will:
1. Install required tools
2. Clean previous builds
3. Build the package
4. Check the package
5. Guide you through uploading

## Important Notes

### Package Name
- The package is named `pearl-rl` (not just `pearl`) to avoid conflicts
- Users will install it with: `pip install pearl-rl`
- Import it with: `import pearl`

### Version Management
- Update version numbers in:
  - `setup.py`
  - `pyproject.toml`
  - `__init__.py`
- Use semantic versioning (e.g., 0.1.0, 0.1.1, 1.0.0)

### Dependencies
- Core dependencies are listed in `pyproject.toml`
- All dependencies from `requirements.txt` are included
- Consider which dependencies are truly required vs optional

## Troubleshooting

### Common Issues

1. **Package name already taken**: Try a different name or add your username
2. **Missing dependencies**: Ensure all imports are available
3. **Build errors**: Check that all files are properly included
4. **Upload errors**: Verify your API tokens and credentials

### Getting Help

- [PyPI Help](https://pypi.org/help/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)

## After Publishing

1. **Verify Installation**: Test installation on a clean environment
2. **Update Documentation**: Ensure README and docs are accurate
3. **Monitor Issues**: Check for user feedback and issues
4. **Plan Updates**: Consider future versions and improvements

## Security Considerations

- Never commit API tokens to version control
- Use environment variables for sensitive information
- Regularly rotate your API tokens
- Consider using trusted publishing for automated releases

## Next Steps

After successful publication:

1. Create a GitHub repository for your project
2. Set up CI/CD for automated testing and publishing
3. Add comprehensive documentation
4. Create example notebooks and tutorials
5. Set up issue tracking and contribution guidelines 