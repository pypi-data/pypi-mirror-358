# Contributing to Traffic-Aware Route Optimizer

We welcome contributions to the Traffic-Aware Route Optimizer! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check the [existing issues](https://github.com/lutic1/traffic-aware-route-optimizer/issues) to avoid duplicates
2. Create a new issue with a clear title and description
3. Include steps to reproduce the bug or detailed feature requirements
4. Add relevant labels (bug, enhancement, question, etc.)

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/traffic-aware-route-optimizer.git
   cd traffic-aware-route-optimizer
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -e .
   pip install pytest black flake8 mypy
   ```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards
3. **Add tests** for new functionality
4. **Run tests** to ensure everything works:
   ```bash
   pytest tests/
   ```

5. **Format your code**:
   ```bash
   black route_planner/
   flake8 route_planner/
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

## Code Style

We use `black` for code formatting and `flake8` for linting:

```bash
# Format code
black route_planner/ tests/

# Check linting
flake8 route_planner/ tests/
```

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting a PR
- Aim for good test coverage
- Use pytest for testing framework

Run tests with:
```bash
pytest tests/ -v
```

## Documentation

- Update README.md if adding new features
- Add examples for new functionality
- Update docstrings for any modified functions
- Consider adding entries to EXAMPLES.md

## Release Process

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md with new features and fixes
3. Create a new release on GitHub
4. PyPI deployment is handled automatically

## Questions?

If you have questions about contributing, please:
- Open an issue for discussion
- Contact the maintainer: Luis Ticas (luis.ticas1@gmail.com)

Thank you for contributing!
