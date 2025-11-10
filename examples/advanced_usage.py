"""
Advanced usage examples for the backend toolkit.

Demonstrates advanced patterns and integrations.
"""

from contextlib import contextmanager
from typing import Any, Dict

from toolkit.config import ConfigManager, ConfigSchema
from toolkit.errors import ApplicationError, ErrorCode
from toolkit.logging import get_logger

# Advanced Configuration with Schema Validation
print("=" * 60)
print("Configuration Schema Validation")
print("=" * 60)

from pydantic import Field, field_validator


class DatabaseConfig(ConfigSchema):
    """Database configuration schema."""

    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535)
    username: str
    password: str
    pool_size: int = Field(default=10, ge=1, le=100)

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        if not v:
            raise ValueError("Host cannot be empty")
        return v


class AppConfig(ConfigSchema):
    """Complete application configuration schema."""

    name: str
    version: str
    debug: bool = False
    database: DatabaseConfig


# Load and validate configuration
try:
    config_data = {
        "name": "my-app",
        "version": "1.0.0",
        "debug": True,
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "username": "admin",
            "password": "secret",
            "pool_size": 20,
        },
    }

    app_config = AppConfig.from_dict(config_data)
    print(f"Validated Config: {app_config.name} v{app_config.version}")
    print(f"Database: {app_config.database.host}:{app_config.database.port}")
except Exception as e:
    print(f"Configuration validation failed: {e}")

print()

# Advanced Logging Patterns
print("=" * 60)
print("Advanced Logging Patterns")
print("=" * 60)

logger = get_logger(__name__)


@contextmanager
def log_operation(operation: str, **context: Any):
    """Context manager for logging operations with timing."""
    import time

    logger.info(f"Starting {operation}", extra=context)
    start_time = time.time()

    try:
        yield
        duration = time.time() - start_time
        logger.info(
            f"Completed {operation}",
            extra={**context, "duration_ms": duration * 1000},
        )
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Failed {operation}",
            extra={**context, "duration_ms": duration * 1000, "error": str(e)},
        )
        raise


# Use the logging context manager
with log_operation("database_query", query="SELECT * FROM users", limit=10):
    # Simulate some work
    import time

    time.sleep(0.1)
    print("Query executed")

print()

# Advanced Error Handling
print("=" * 60)
print("Advanced Error Handling")
print("=" * 60)


class ServiceError(ApplicationError):
    """Base error for service layer."""

    category = ApplicationError.category


class ExternalServiceError(ServiceError):
    """Error from external service."""

    code = ErrorCode.EXTERNAL


def retry_on_error(max_retries: int = 3, backoff: float = 1.0):
    """Decorator for retrying functions on error."""
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        sleep_time = backoff * (2**attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {sleep_time}s",
                            extra={"error": str(e)},
                        )
                        time.sleep(sleep_time)

            raise last_error

        return wrapper

    return decorator


@retry_on_error(max_retries=3, backoff=0.5)
def fetch_external_data():
    """Example function with retry logic."""
    # Simulate external API call
    print("Fetching data from external service...")
    return {"status": "success", "data": [1, 2, 3]}


try:
    result = fetch_external_data()
    print(f"Result: {result}")
except Exception as e:
    logger.exception("Failed to fetch external data")

print()

# Error Registry and Monitoring
print("=" * 60)
print("Error Registry and Monitoring")
print("=" * 60)

from toolkit.errors import ErrorRegistry

registry = ErrorRegistry()

# Register custom errors
registry.register(ValidationError)
registry.register(DatabaseError)


def track_error(error: ApplicationError) -> None:
    """Track error occurrence."""
    registry.record_occurrence(error)
    logger.error(
        f"Error tracked: {error.code}",
        extra={"category": error.category, "details": error.details},
    )


# Simulate some errors
for _ in range(3):
    error = ValidationError("Invalid input")
    track_error(error)

for _ in range(2):
    error = DatabaseError("Connection failed")
    track_error(error)

# Get statistics
stats = registry.get_statistics()
print(f"Error Statistics: {stats}")

print()

# Configuration Hot-Reloading
print("=" * 60)
print("Configuration Hot-Reloading")
print("=" * 60)


class ConfigurableService:
    """Service that supports configuration hot-reloading."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = ConfigManager.from_yaml(config_path)
        self.logger = get_logger(self.__class__.__name__)

    def reload_config(self) -> None:
        """Reload configuration from file."""
        try:
            self.config.reload(self.config_path)
            self.logger.info("Configuration reloaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get configuration setting."""
        return self.config.get(key, default)


# Example service
service = ConfigurableService("configs/config.yaml")
print(f"Initial setting: {service.get_setting('app.name')}")

# In production, you might reload on signal or periodic check
# service.reload_config()

print()

# Composable Modules Example
print("=" * 60)
print("Composable Modules Example")
print("=" * 60)


class DatabaseClient:
    """Example database client using toolkit modules."""

    def __init__(self, config: ConfigManager, logger: Any):
        self.config = config
        self.logger = logger
        self.host = config.get("database.host")
        self.port = config.get_int("database.port")

    def connect(self):
        """Connect to database."""
        try:
            self.logger.info(
                "Connecting to database", extra={"host": self.host, "port": self.port}
            )
            # Connection logic here
            return True
        except Exception as e:
            raise DatabaseError(
                "Failed to connect",
                code=ErrorCode.DATABASE_CONNECTION,
                details={"host": self.host, "port": self.port},
                cause=e,
            )


class CacheClient:
    """Example cache client using toolkit modules."""

    def __init__(self, config: ConfigManager, logger: Any):
        self.config = config
        self.logger = logger
        self.host = config.get("cache.host")
        self.ttl = config.get_int("cache.ttl")

    def get(self, key: str) -> Any:
        """Get cached value."""
        self.logger.debug("Cache lookup", extra={"key": key})
        # Cache logic here
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        self.logger.debug("Cache set", extra={"key": key, "ttl": self.ttl})
        # Cache logic here
        pass


# Compose services
config = ConfigManager.from_yaml("configs/config.yaml")
logger = get_logger("services")

db = DatabaseClient(config, logger)
cache = CacheClient(config, logger)

print("Services initialized with shared configuration and logging")

print()
print("=" * 60)
print("All advanced examples completed!")
print("=" * 60)
