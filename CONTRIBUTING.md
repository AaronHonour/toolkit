# Contributing to Backend Toolkit

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd toolkit
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Development Workflow

### Code Style

We follow PEP 8 and use automated tools:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/toolkit --cov-report=html

# Run specific test file
pytest tests/test_config/test_manager.py

# Run with verbose output
pytest -v
```

### Adding New Features

1. **Design First**: Consider how it fits into the architecture
2. **Configuration**: Make it configurable via YAML
3. **Type Hints**: Add complete type annotations
4. **Documentation**: Add docstrings and examples
5. **Tests**: Write comprehensive tests
6. **Examples**: Add usage examples

### Module Checklist

When adding a new module:

- [ ] Module directory under `src/toolkit/`
- [ ] `__init__.py` with exports
- [ ] Core implementation files
- [ ] Configuration schema
- [ ] Example YAML config in `configs/`
- [ ] Unit tests in `tests/test_<module>/`
- [ ] Integration examples in `examples/`
- [ ] Documentation in docstrings
- [ ] Update main README.md

### Code Review Guidelines

- **Readability**: Code should be self-documenting
- **Simplicity**: Avoid over-engineering
- **Performance**: Consider optimization opportunities
- **Security**: Check for vulnerabilities
- **Testing**: Ensure adequate test coverage
- **Documentation**: Update docs as needed

## Architecture Guidelines

### Composability
- Modules should work independently
- Avoid tight coupling
- Use dependency injection

### Configuration-Driven
- No hardcoded values
- Support environment variables
- Provide sensible defaults

### Type Safety
- Use type hints everywhere
- Validate at runtime when appropriate
- Use Pydantic for complex validation

### Performance
- Profile before optimizing
- Cache intelligently
- Consider thread safety

### Enterprise Features
- Comprehensive error handling
- Structured logging
- Security considerations
- Extensibility

## Testing Standards

### Test Coverage
- Aim for >90% coverage
- Test happy paths and edge cases
- Test error conditions
- Test thread safety when relevant

### Test Organization
```
tests/
├── conftest.py              # Shared fixtures
├── test_<module>/
│   ├── __init__.py
│   ├── test_<component>.py
│   └── fixtures/            # Test data
```

### Test Naming
- Test classes: `TestClassName`
- Test methods: `test_what_is_being_tested`
- Be descriptive and specific

### Fixtures
- Use pytest fixtures for reusable test data
- Keep fixtures in `conftest.py` if shared
- Local fixtures for module-specific needs

## Documentation Standards

### Docstrings
Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Brief description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is invalid

    Examples:
        >>> function("test", 42)
        True
    """
```

### Comments
- Explain **why**, not **what**
- Keep comments up-to-date
- Remove dead code instead of commenting it out

## Git Workflow

### Branches
- `main`: Stable release branch
- `develop`: Development branch
- `feature/name`: New features
- `fix/name`: Bug fixes
- `docs/name`: Documentation updates

### Commit Messages
Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(config): add hot-reload support
fix(logging): correct thread safety issue
docs(readme): update installation instructions
```

### Pull Requests
1. Create feature branch from `develop`
2. Make changes with tests
3. Update documentation
4. Create PR with clear description
5. Address review feedback
6. Squash and merge

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Create release tag
5. Build and publish to PyPI

## Questions?

- Open an issue for bugs
- Use discussions for questions
- Check existing issues before creating new ones

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Keep discussions on topic
