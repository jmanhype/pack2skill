# PyPI Publishing Guide for pack2skill

This guide walks you through publishing pack2skill to PyPI (Python Package Index).

## Prerequisites

1. **Create PyPI Account**: Register at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **Create TestPyPI Account**: Register at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
3. **Install Build Tools**:
   ```bash
   pip install --upgrade build twine
   ```

## Step 1: Verify Package Configuration

Check that all files are correct:

```bash
# Verify setup.py
python setup.py check

# Verify package structure
python -c "from setuptools import find_packages; print(find_packages())"
```

## Step 2: Build the Distribution

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/pack2skill-0.1.0.tar.gz` (source distribution)
- `dist/pack2skill-0.1.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pack2skill
```

## Step 4: Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Step 5: Verify Installation

```bash
# Install from PyPI
pip install pack2skill

# Test the CLI
pack2skill --version
python -m pack2skill --help
```

## Using API Tokens (Recommended)

For better security, use API tokens instead of passwords:

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to "API tokens" and click "Add API token"
3. Set scope to "Entire account" or specific project
4. Copy the token (starts with `pypi-`)

### Configure Credentials

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

Set permissions:
```bash
chmod 600 ~/.pypirc
```

## Automated Publishing with GitHub Actions

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
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Version Management

### Bumping Versions

For new releases, update version in:
1. `setup.py` - line 22
2. `pyproject.toml` - line 6

Version scheme (semantic versioning):
- **Patch** (0.1.0 → 0.1.1): Bug fixes
- **Minor** (0.1.0 → 0.2.0): New features, backward compatible
- **Major** (0.1.0 → 1.0.0): Breaking changes

### Release Checklist

- [ ] Update version numbers in `setup.py` and `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run tests: `pytest`
- [ ] Build and test locally: `python -m build`
- [ ] Test on TestPyPI
- [ ] Create git tag: `git tag v0.1.0`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Publish to PyPI
- [ ] Create GitHub release with changelog

## Troubleshooting

### "File already exists" Error

If you get this error, the version already exists on PyPI. You must:
1. Increment the version number
2. Rebuild the package
3. Upload again

### Import Errors After Installation

Ensure all dependencies are listed in `requirements.txt` and `setup.py`.

### Missing Files in Distribution

Check `MANIFEST.in` and ensure all necessary files are included:

```
include README.md
include LICENSE
include requirements.txt
recursive-include pack2skill *.py
recursive-include docs *.md
```

## Resources

- [PyPI Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging User Guide](https://packaging.python.org/)
