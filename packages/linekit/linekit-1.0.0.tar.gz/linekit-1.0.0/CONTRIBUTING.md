# Contributing to LINE API Integration Library

Thank you for your interest in contributing to the LINE API Integration Library! We appreciate your time and effort in making this project better.

## Getting Started

1. **Fork the repository** and clone it locally.

2. **Set up the development environment**:

   ```bash
   # Create a virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Create a new branch** for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We use `ruff` for code formatting and linting. Please ensure your code follows these guidelines:

```bash
# Run the linter
ruff check .

# Format code
ruff format .
```

### Type Checking

We use `mypy` for static type checking. Run the following to check for type errors:

```bash
mypy line_api tests
```

### Testing

We use `pytest` for testing. To run the tests:

```bash
pytest tests/
```

### Documentation

- Update any relevant documentation when adding new features or changing existing functionality.
- Use Google-style docstrings for all public functions and classes.

## Pull Request Process

1. Ensure all tests pass and there are no linting errors.
2. Update the README.md with details of changes if needed.
3. Submit a pull request with a clear description of the changes and the problem/feature they address.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

By contributing to this project, you agree that your contributions will be licensed under its MIT License.
