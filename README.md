# Backend Toolkit

Enterprise-grade Python toolkit for backend development with a focus on composability, performance, and configuration-driven architecture.

## Features

- **Configuration Management**: YAML-driven configuration with validation, environment variable interpolation, and hot-reloading
- **Advanced Logging**: Structured logging with multiple handlers, formatters, and filters
- **Error Handling**: Comprehensive error system with custom exceptions, error codes, and handlers
- **Environment Management**: Multi-environment support with validation and type-safe access

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### Configuration Management

```python
from toolkit.config import ConfigManager

# Load from YAML
config = ConfigManager.from_yaml("configs/config.yaml")

# Access nested values
db_host = config.get("database.host", default="localhost")

# Type-safe access
db_port = config.get_int("database.port", default=5432)
```

### Logging

```python
from toolkit.logging import LoggerFactory

# Create logger from config
logger = LoggerFactory.from_yaml("configs/logging.yaml")

# Use structured logging
logger.info("User login", extra={"user_id": 123, "ip": "192.168.1.1"})
```

### Error Handling

```python
from toolkit.errors import ApplicationError, ErrorCode

# Define custom errors
class DatabaseError(ApplicationError):
    code = ErrorCode.DATABASE_ERROR

# Use in code
try:
    # ... database operation
    raise DatabaseError("Connection failed", details={"host": "localhost"})
except ApplicationError as e:
    logger.error(f"Error: {e.code} - {e.message}", extra=e.details)
```

### Environment Management

```python
from toolkit.env import EnvManager

# Load environment configuration
env = EnvManager.from_yaml("configs/env.yaml")

# Access with validation
api_key = env.require("API_KEY")  # Raises if missing
debug_mode = env.get_bool("DEBUG", default=False)
```

## Architecture

The toolkit follows SOLID principles and emphasizes:

- **Composability**: Each module works independently or together
- **Configuration-driven**: Everything configurable via YAML
- **Performance**: Lazy loading, caching, minimal overhead
- **Type Safety**: Full type hints and runtime validation
- **Enterprise-ready**: Thread-safe, production-tested patterns

## Project Structure

```
toolkit/
├── src/toolkit/          # Main package
│   ├── config/          # Configuration management
│   ├── logging/         # Logging system
│   ├── errors/          # Error handling
│   └── env/             # Environment management
├── configs/             # Example configurations
├── tests/               # Comprehensive tests
└── examples/            # Usage examples
```

## Configuration Files

All modules are configured via YAML files in the `configs/` directory:

- `config.yaml` - Application configuration
- `logging.yaml` - Logging setup
- `errors.yaml` - Error handling rules
- `env.yaml` - Environment variables

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src/ tests/
ruff check src/ tests/
```

Type checking:
```bash
mypy src/
```

## License

MIT
