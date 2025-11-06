# Contributing to Pack2Skill

Thank you for your interest in contributing to Pack2Skill! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Report bugs**: Open an issue describing the bug and how to reproduce it
- **Suggest features**: Share your ideas for new features or improvements
- **Improve documentation**: Fix typos, clarify instructions, add examples
- **Submit code**: Fix bugs, implement features, or improve performance
- **Share skills**: Contribute high-quality skills to the community

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/pack2skill.git
   cd pack2skill
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where applicable
- Add docstrings to all public functions and classes
- Keep functions focused and modular

### Testing

- Add tests for new features
- Ensure all existing tests pass:
  ```bash
  pytest tests/ -v
  ```
- Aim for good test coverage

### Documentation

- Update documentation for new features
- Add examples for complex functionality
- Keep the README and user guide up to date

## Submitting Changes

1. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what it does"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes
   - Reference any related issues

### Pull Request Guidelines

- **One feature per PR**: Keep changes focused
- **Write clear descriptions**: Explain what, why, and how
- **Include tests**: Add tests for new functionality
- **Update documentation**: Keep docs in sync with code
- **Follow the code style**: Match the existing code conventions

## Issue Guidelines

### Reporting Bugs

Include:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Features

Include:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach (optional)

## Development Setup

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=pack2skill --cov-report=html

# Run specific test file
pytest tests/test_generator.py -v
```

### Code Formatting

We recommend using `black` for code formatting:

```bash
# Install black
pip install black

# Format code
black pack2skill/
```

### Type Checking

We use `mypy` for type checking:

```bash
# Install mypy
pip install mypy

# Check types
mypy pack2skill/
```

## Project Structure

```
pack2skill/
├── pack2skill/          # Main package
│   ├── core/           # Core functionality (Phase 1)
│   ├── quality/        # Quality improvements (Phase 2)
│   ├── team/           # Team features (Phase 3)
│   ├── ecosystem/      # Ecosystem integration (Phase 4)
│   └── cli/            # Command-line interface
├── tests/              # Test suite
├── examples/           # Example scripts
└── docs/               # Documentation
```

## Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and PRs where appropriate

Examples:
```
Add confidence scoring for workflow steps
Fix frame extraction on Windows
Update documentation for CLI commands
```

## Community

- Be respectful and inclusive
- Help others in discussions and issues
- Share your experiences and use cases
- Follow our Code of Conduct

## Questions?

- Open an issue for questions about contributing
- Check existing issues and discussions
- Read the documentation in `/docs`

## License

By contributing to Pack2Skill, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Pack2Skill! Your help makes this project better for everyone.
