# Contributing to WRD

Thank you for your interest in contributing to WRD! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/your-wronai/wrd.git
   cd wrd
   ```
3. **Set up the development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]  # Install development dependencies
   ```

## Development Workflow

1. **Create a new branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure tests pass
   ```bash
   # Run tests
   pytest tests/
   
   # Run linter
   flake8 wrd
   
   # Run type checker
   mypy wrd
   ```

3. **Commit your changes** with a descriptive message
   ```bash
   git commit -m "Add new feature: your feature description"
   ```

4. **Push to your fork** and open a pull request

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep lines under 88 characters (Black will handle this)

## Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a pull request
- Use descriptive test function names that describe what's being tested

## Reporting Issues

When reporting issues, please include:

1. A clear description of the problem
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Any relevant error messages or logs
5. Your operating system and Python version

## Code Review Process

1. Create a pull request with your changes
2. Ensure all CI checks pass
3. A maintainer will review your changes and provide feedback
4. Once approved, your changes will be merged into the main branch

## License

By contributing to WRD, you agree that your contributions will be licensed under the MIT License.
