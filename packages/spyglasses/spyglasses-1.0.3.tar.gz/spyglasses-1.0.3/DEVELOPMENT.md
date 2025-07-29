# Development Guide

This guide covers development setup, testing, and contribution guidelines for the Spyglasses Python SDK.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Setting up the Development Environment

1. **Clone the repository**:
```bash
git clone https://github.com/orchestra-code/spyglasses-python.git
cd spyglasses-python
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the package in development mode**:
```bash
pip install -e ".[dev]"
```

This installs the package in editable mode with all development dependencies including:
- `pytest` for testing
- `pytest-cov` for coverage
- `pytest-asyncio` for async testing
- `black` for code formatting
- `ruff` for linting
- `mypy` for type checking
- `httpx` for async HTTP testing

### Environment Variables

Create a `.env` file for development:

```bash
SPYGLASSES_API_KEY=your-development-api-key
SPYGLASSES_DEBUG=true
SPYGLASSES_AUTO_SYNC=false  # Disable auto-sync during development
```

## Project Structure

```
spyglasses-python/
├── src/spyglasses/           # Main package source code
│   ├── __init__.py          # Package initialization and exports
│   ├── client.py            # Core detection client
│   ├── configuration.py     # Configuration management
│   ├── exceptions.py        # Custom exceptions
│   ├── types.py            # Type definitions and data classes
│   └── middleware/         # Framework integrations
│       ├── __init__.py
│       ├── base.py         # Base middleware class
│       ├── django.py       # Django middleware
│       ├── flask.py        # Flask middleware
│       ├── fastapi.py      # FastAPI middleware
│       ├── wsgi.py         # WSGI middleware
│       └── asgi.py         # ASGI middleware
├── tests/                  # Test suite
├── pyproject.toml         # Package configuration
├── README.md              # Main documentation
├── CHANGELOG.md           # Version history
└── DEVELOPMENT.md         # This file
```

## Development Workflow

### 1. Code Formatting

Run Black to format code:
```bash
black src/ tests/
```

### 2. Linting

Run Ruff to check for code issues:
```bash
ruff check src/ tests/
```

Fix auto-fixable issues:
```bash
ruff check --fix src/ tests/
```

### 3. Type Checking

Run MyPy for type checking:
```bash
mypy src/
```

### 4. Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=spyglasses --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v

# Run only fast tests (exclude slow/integration tests)
pytest -m "not slow"
```

### 5. Pre-commit Checks

Before committing, run all checks:
```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Type check
mypy src/

# Run tests
pytest
```

## Testing Guidelines

### Test Organization

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Framework tests**: Test middleware integrations (may require optional dependencies)

### Test Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Mocking External Services

Use pytest fixtures and mocking for external API calls:

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_api_response():
    return {
        "version": "1.0.0",
        "patterns": [...],
        "ai_referrers": [...],
        "property_settings": {...}
    }

def test_sync_patterns(mock_api_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_api_response
        # Test sync_patterns functionality
```

### Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.slow
def test_heavy_operation():
    """Test that takes a long time."""
    pass

@pytest.mark.integration
def test_api_integration():
    """Test that requires external API."""
    pass
```

## Adding New Features

### 1. Framework Middleware

To add support for a new framework:

1. Create `src/spyglasses/middleware/new_framework.py`
2. Extend `BaseMiddleware`
3. Implement framework-specific request/response handling
4. Add optional import to `src/spyglasses/middleware/__init__.py`
5. Add framework to `pyproject.toml` optional dependencies
6. Write tests in `tests/test_middleware_new_framework.py`
7. Update documentation

### 2. Detection Logic

To modify detection logic:

1. Update `src/spyglasses/client.py`
2. Add new patterns to `_load_default_patterns()`
3. Update `src/spyglasses/types.py` if new data structures are needed
4. Write comprehensive tests
5. Update documentation

### 3. Configuration Options

To add new configuration options:

1. Update `src/spyglasses/configuration.py`
2. Add environment variable support
3. Update type hints and validation
4. Document the new option
5. Write tests

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use Black for formatting (line length: 88 characters)
- Use type hints for all public APIs
- Use docstrings for all public functions and classes

### Docstring Format

Use Google-style docstrings:

```python
def detect_bot(self, user_agent: Optional[str]) -> DetectionResult:
    """
    Detect if a user agent is a bot.
    
    Args:
        user_agent: User agent string to check
        
    Returns:
        DetectionResult with bot detection results
        
    Raises:
        ValueError: If user_agent format is invalid
    """
```

### Error Handling

- Use custom exceptions from `exceptions.py`
- Always handle network errors gracefully
- Log errors appropriately using the built-in debug logging
- Never let SDK errors crash the host application

### Thread Safety

- Use locks for shared mutable state
- Be careful with regex cache updates
- Consider async/await patterns for I/O operations

## Building and Publishing

### Build Package

```bash
# Install build tools
pip install build

# Build package
python -m build
```

This creates wheel and source distributions in `dist/`.

### Version Management

Update version in `src/spyglasses/__init__.py`:

```python
__version__ = "1.1.0"
```

### Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to test PyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Documentation

### API Documentation

- Use clear docstrings with type hints
- Include examples in docstrings
- Document all public APIs

### README Updates

When adding features:
1. Update the feature list
2. Add usage examples
3. Update installation instructions if needed

### Changelog

Follow [Keep a Changelog](https://keepachangelog.com/):
- Add entries to `CHANGELOG.md`
- Use semantic versioning
- Document breaking changes clearly

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all checks pass
5. Update documentation
6. Submit pull request

### Commit Messages

Use clear, descriptive commit messages:
- `feat: add FastAPI middleware support`
- `fix: handle empty user agent strings`
- `docs: update installation instructions`
- `test: add integration tests for Django middleware`

### Code Review

All changes require code review. Reviewers check for:
- Code quality and style
- Test coverage
- Documentation updates
- Breaking change considerations
- Performance implications

## Debugging

### Debug Logging

Enable debug logging to see detailed information:

```python
import spyglasses

config = spyglasses.Configuration(debug=True)
client = spyglasses.Client(config)
```

Or via environment variable:
```bash
export SPYGLASSES_DEBUG=true
```

### Common Issues

1. **Import Errors**: Ensure optional dependencies are installed
2. **API Errors**: Check API key and network connectivity
3. **Blocking Issues**: Review custom rules and pattern matching
4. **Performance**: Check pattern cache and auto-sync settings

## Support

- Create issues on GitHub for bugs or feature requests
- Use discussions for questions and community support
- Check existing issues before creating new ones 