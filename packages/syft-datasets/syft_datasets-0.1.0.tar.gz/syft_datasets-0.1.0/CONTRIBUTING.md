# Contributing to Syft-Datasets

Thank you for your interest in contributing to Syft-Datasets! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/syft-datasets.git
   cd syft-datasets
   ```

3. **Set up development environment**:
   ```bash
   # Using pip
   pip install -e ".[dev]"
   
   # Or using uv (recommended)
   uv sync --group dev
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Verify setup** by running tests:
   ```bash
   pytest
   ```

## 📝 Development Workflow

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Add tests** for any new functionality

4. **Run tests and checks**:
   ```bash
   # Run tests
   pytest
   
   # Run linting
   ruff check
   
   # Format code
   ruff format
   
   # Type checking (optional but recommended)
   mypy syft_datasets/
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

### Commit Message Guidelines

Use clear, descriptive commit messages:

- **feat**: New features
- **fix**: Bug fixes
- **docs**: Documentation changes
- **test**: Adding or updating tests
- **refactor**: Code refactoring
- **style**: Code style changes
- **ci**: CI/CD changes

Examples:
```feat: add search functionality to dataset collection
fix: handle empty dataset collections gracefully
docs: update README with new API examples
test: add tests for dataset filtering
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=syft_datasets

# Run specific test file
pytest tests/test_datasets.py

# Run tests matching pattern
pytest -k "test_search"
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Include both positive and negative test cases
- Mock external dependencies (SyftBox, network calls)

Example test structure:
```python
def test_feature_name():
    """Test description of what this test verifies."""
    # Arrange
    setup_data = create_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

## 🎨 Code Style

### Python Style Guidelines

- Follow **PEP 8** conventions
- Use **type hints** for function parameters and return values
- Write **docstrings** for classes and functions
- Keep line length under **100 characters**
- Use **descriptive variable names**

### Code Formatting

We use `ruff` for both linting and formatting:

```bash
# Auto-format code
ruff format

# Check for linting issues
ruff check

# Fix auto-fixable issues
ruff check --fix
```

### Type Hints

Include type hints for better code documentation:

```python
from typing import List, Optional

def search_datasets(
    query: str, 
    datasets: List[Dataset]
) -> List[Dataset]:
    """Search datasets by query string."""
    return [ds for ds in datasets if query.lower() in ds.name.lower()]
```

## 📚 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> bool:
    """One-line summary of the function.

    Longer description if needed, explaining the purpose
    and behavior of the function.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When param2 is negative.
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return len(param1) > param2
```

### README Updates

If your changes affect user-facing functionality:
- Update relevant sections in `README.md`
- Add new examples if introducing new features
- Update the API reference section

## 🐛 Bug Reports

When reporting bugs, include:

1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Python version
   - Package versions (`pip freeze`)
   - Operating system
5. **Code examples** or error messages

Use the bug report template when creating issues.

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and motivation
3. **Propose an API design** if applicable
4. **Consider backwards compatibility**
5. **Offer to implement** if you're able

## 🔍 Code Review Process

### For Contributors

- Ensure all tests pass
- Keep PRs focused on a single feature/fix
- Include tests for new functionality
- Update documentation as needed
- Respond to review feedback promptly

### For Reviewers

- Be constructive and respectful
- Focus on code quality and maintainability
- Check for test coverage
- Verify documentation updates
- Test the changes locally when possible

## 🏷️ Release Process

Releases are managed by maintainers:

1. **Version bumping** follows semantic versioning
2. **Changelog** is updated with notable changes
3. **GitHub releases** are created with release notes
4. **PyPI publishing** is automated via GitHub Actions

## 📞 Getting Help

If you need help:

- **Check existing issues** and documentation
- **Ask questions** in GitHub Discussions
- **Join the Discord** community for real-time help
- **Tag maintainers** in issues or PRs if needed

## 🏆 Recognition

Contributors are recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

## 📜 Code of Conduct

This project follows the OpenMined Code of Conduct. Please be respectful and inclusive in all interactions.

## 🔧 Development Tips

### Useful Commands

```bash
# Install package in development mode
pip install -e ".[dev]"

# Run all checks before committing
ruff check && ruff format && pytest

# Update dependencies
pip freeze > requirements.txt

# Check for security issues
pip audit
```

### IDE Setup

For VS Code, recommended extensions:
- Python
- Pylance
- Ruff
- pytest

For PyCharm:
- Enable type checking
- Configure Ruff as external tool
- Set up pytest as test runner

### Debugging

For debugging issues:
- Use `pytest -v -s` for verbose output
- Add `breakpoint()` for debugging
- Use `pytest --pdb` to drop into debugger on failures
- Check logs and connection status when working with SyftBox

---

Thank you for contributing to Syft-Datasets! 🎉 

## 🚀 How to Make Your First Release

### 1. Test Everything Locally First
```bash
cd syft-datasets

# Install in development mode
pip install -e ".[dev]"

# Run all checks
pytest
ruff check && ruff format
python -m build

# Test the built package
pip install dist/syft_datasets-0.1.0-py3-none-any.whl --force-reinstall
```

### 2. Push to GitHub
```bash
git add .
git commit -m "feat: ready for first release"
git push origin main
```

### 3. Create GitHub Release
1. **Go to your repo** → **Releases** → **Create a new release**
2. **Tag version**: `v0.1.0` (creates the tag)
3. **Release title**: `v0.1.0 - Initial Release`
4. **Description**:
   ```markdown
   🎉 First release of syft-datasets!

   ## Features
   - Interactive dataset discovery with beautiful Jupyter UI
   - Search and filter datasets across SyftBox datasites
   - Checkbox selection with automatic code generation

   ## Installation
   ```bash
   pip install syft-datasets
   ```
   ```

5. **Click "Publish release"** ✨

### 4. Watch the Magic Happen!
- GitHub Action will **automatically trigger**
- Build and test your package
- **Publish to PyPI** (if setup correctly)
- Users can then: `pip install syft-datasets`

## 🔍 Troubleshooting

### Check Dependencies
Make sure these packages exist on PyPI (you might need to adjust versions):
```toml
dependencies = [
    "syft-core>=0.2.0",     # ⚠️ Check if this exists on PyPI
    "syft-rds>=0.1.0",      # ⚠️ Check if this exists on PyPI
    "pandas>=1.3.0",
    "tabulate>=0.9.0", 
    "requests>=2.25.0",
]
```

If the `syft-*` packages aren't on PyPI yet, you might need to:
- Publish those first, or
- Make them optional dependencies, or
- Adjust version requirements

### Test on TestPyPI First
For safety, test on TestPyPI first by modifying the workflow temporarily:

```yaml
- name: Publish to TestPyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    repository-url: https://test.pypi.org/legacy/
    print-hash: true
```

## ✅ Your Setup is Ready!

You now have:
- ✅ **Automated PyPI publishing** on GitHub releases
- ✅ **Professional CI/CD pipeline** 
- ✅ **Quality checks** before publishing
- ✅ **Modern trusted publishing** (most secure method)

Just **create a GitHub release** and watch it automatically publish to PyPI! 🎉 