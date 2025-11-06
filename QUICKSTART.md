# Quick Start Guide

Get up and running with Backend Toolkit in 5 minutes.

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Basic Setup

### 1. Create Configuration File

Create `config.yaml`:

```yaml
app:
  name: my-app
  version: 1.0.0

database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  name: myapp
```

### 2. Create Environment File

Create `.env`:

```bash
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
```

### 3. Write Your Application

```python
from toolkit.config import ConfigManager
from toolkit.logging import LoggerFactory
from toolkit.env import EnvManager

# Load configuration
config = ConfigManager.from_yaml("config.yaml")

# Setup logging
logger = LoggerFactory.create("my-app", level="INFO")

# Setup environment
env = EnvManager()

# Use the toolkit
app_name = config.get("app.name")
db_host = config.get("database.host")
secret = env.require("SECRET_KEY")

logger.info(f"Starting {app_name}", extra={"host": db_host})
```

## Common Use Cases

### Configuration Management

```python
from toolkit.config import ConfigManager

# Load from YAML
config = ConfigManager.from_yaml("config.yaml")

# Access nested values
db_host = config.get("database.host", default="localhost")
db_port = config.get_int("database.port", default=5432)

# Get lists and dicts
features = config.get_list("features")
settings = config.get_dict("settings")

# Require values
api_key = config.require("api.key")  # Raises if missing

# Update configuration
config.set("app.version", "1.0.1")
```

### Logging

```python
from toolkit.logging import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Application started")
logger.error("Error occurred", exc_info=True)

# Structured logging
logger.info("User login", extra={
    "user_id": 123,
    "ip": "192.168.1.1",
    "action": "login"
})

# Set context (included in all logs)
logger.set_context(request_id="abc-123")
logger.info("Processing request")
logger.clear_context()
```

### Error Handling

```python
from toolkit.errors import ValidationError, ErrorCode

# Raise typed errors
raise ValidationError(
    "Invalid email format",
    code=ErrorCode.INVALID_FORMAT,
    details={"field": "email", "value": "invalid"}
)

# Handle errors
try:
    # Your code
    pass
except ValidationError as e:
    logger.error(f"Validation failed: {e.message}", extra=e.details)
    print(f"Error code: {e.code}")
    print(f"Error dict: {e.to_dict()}")
```

### Environment Management

```python
from toolkit.env import EnvManager

env = EnvManager()

# Get with type conversion
port = env.get_int("PORT", default=8000)
debug = env.get_bool("DEBUG", default=False)
hosts = env.get_list("ALLOWED_HOSTS")

# Require variables
api_key = env.require("API_KEY")  # Raises if not set

# Check environment
if env.is_production():
    # Production logic
    pass
```

## Complete Application Example

```python
from toolkit.config import ConfigManager
from toolkit.logging import LoggerFactory
from toolkit.errors import ApplicationError
from toolkit.env import EnvManager


class Application:
    def __init__(self):
        # Initialize all modules
        self.config = ConfigManager.from_yaml("config.yaml")
        self.logger = LoggerFactory.from_yaml("logging.yaml")
        self.env = EnvManager.from_yaml("env.yaml")

        # Set logging context
        self.logger.set_context(
            app_name=self.config.get("app.name"),
            environment=self.env.get_environment().value
        )

        self.logger.info("Application initialized")

    def run(self):
        try:
            # Validate required environment variables
            self.env.validate_required()

            # Your application logic
            self.logger.info("Application running")

        except ApplicationError as e:
            self.logger.error(f"Error: {e.code} - {e.message}", extra=e.details)
        except Exception as e:
            self.logger.exception("Unexpected error")
        finally:
            self.logger.info("Application shutdown")


if __name__ == "__main__":
    app = Application()
    app.run()
```

## Configuration Files

### Logging Configuration

Create `logging.yaml`:

```yaml
name: app
level: INFO

handlers:
  - type: console
    level: INFO
    stream: stdout
    formatter: structured

  - type: rotating_file
    level: INFO
    filename: logs/app.log
    max_bytes: 10485760  # 10MB
    backup_count: 5
    compress: true
    formatter: json

filters:
  - type: sensitive_data
```

### Environment Configuration

Create `env.yaml`:

```yaml
env_file: .env
environment: ${ENV:development}

required:
  - SECRET_KEY
  - DATABASE_URL
```

## Next Steps

1. Read the [Architecture Guide](ARCHITECTURE.md)
2. Check [Examples](examples/) for advanced patterns
3. Review [Contributing Guide](CONTRIBUTING.md)
4. Run the test suite: `pytest`

## Tips

- Use environment variables for secrets
- Enable structured logging for production
- Configure sensitive data filters
- Use type-safe getters to catch errors early
- Set up error handlers for monitoring
- Use context in logging for request correlation

## Getting Help

- Check the examples directory
- Read the module docstrings
- Open an issue on GitHub
- Review the test cases for usage patterns
