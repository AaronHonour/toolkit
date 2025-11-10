"""
Basic usage examples for the backend toolkit.

Demonstrates how to use configuration, logging, errors, and environment modules.
"""

from pathlib import Path

# Configuration Management
from toolkit.config import ConfigManager

print("=" * 60)
print("Configuration Management Example")
print("=" * 60)

# Load configuration from YAML
config = ConfigManager.from_yaml("configs/config.yaml")

# Access nested values with dot notation
app_name = config.get("app.name")
db_host = config.get("database.host", default="localhost")
db_port = config.get_int("database.port", default=5432)

print(f"App Name: {app_name}")
print(f"Database: {db_host}:{db_port}")

# Get list values
cors_origins = config.get_list("api.cors.origins", default=[])
print(f"CORS Origins: {cors_origins}")

# Set values
config.set("app.version", "1.0.1")

print()

# Logging
from toolkit.logging import LoggerFactory, get_logger

print("=" * 60)
print("Logging Example")
print("=" * 60)

# Create logger from config
logger = LoggerFactory.from_yaml("configs/logging.yaml")

# Basic logging
logger.info("Application started")
logger.debug("Debug information", extra={"user_id": 123})
logger.warning("Warning message")

# Structured logging with context
logger.set_context(request_id="abc-123", user_id=456)
logger.info("Processing request")

# Log with additional context
logger.info("User action", extra={"action": "login", "ip": "192.168.1.1"})

# Clear context
logger.clear_context()

print()

# Error Handling
from toolkit.errors import (
    ApplicationError,
    ValidationError,
    DatabaseError,
    NotFoundError,
    ErrorCode,
)

print("=" * 60)
print("Error Handling Example")
print("=" * 60)


def validate_user_input(data: dict) -> None:
    """Example function that validates user input."""
    if "email" not in data:
        raise ValidationError(
            "Email is required",
            code=ErrorCode.MISSING_REQUIRED,
            details={"field": "email"},
        )


try:
    validate_user_input({"name": "John"})
except ValidationError as e:
    print(f"Validation Error: {e}")
    print(f"Error Code: {e.code}")
    print(f"Details: {e.details}")
    print(f"Dictionary: {e.to_dict()}")

print()

# Custom error with context
try:
    raise DatabaseError(
        "Failed to connect to database",
        code=ErrorCode.DATABASE_CONNECTION,
        details={"host": "localhost", "port": 5432},
    )
except DatabaseError as e:
    logger.error(f"Database error: {e.message}", extra=e.details)

print()

# Error handlers
from toolkit.errors import LoggingErrorHandler, ErrorHandlerChain

handler_chain = ErrorHandlerChain()
handler_chain.add_handler(LoggingErrorHandler(logger=logger._logger))

try:
    raise NotFoundError("User not found", details={"user_id": 999})
except ApplicationError as e:
    handler_chain.handle(e, context={"endpoint": "/api/users/999"})

print()

# Environment Management
from toolkit.env import EnvManager, Environment

print("=" * 60)
print("Environment Management Example")
print("=" * 60)

# Create environment manager
env = EnvManager(environment=Environment.DEVELOPMENT)

# Get environment variables with type safety
debug_mode = env.get_bool("DEBUG", default=False)
api_port = env.get_int("API_PORT", default=8000)
log_level = env.get("LOG_LEVEL", default="INFO")

print(f"Debug Mode: {debug_mode}")
print(f"API Port: {api_port}")
print(f"Log Level: {log_level}")

# Check environment
if env.is_development():
    print("Running in DEVELOPMENT mode")

# Get list from environment
allowed_hosts = env.get_list("ALLOWED_HOSTS", default=["localhost"])
print(f"Allowed Hosts: {allowed_hosts}")

# Required variables
try:
    api_key = env.require("API_KEY")
except ValueError as e:
    print(f"Missing required variable: {e}")

print()

# Complete Application Example
print("=" * 60)
print("Complete Application Setup")
print("=" * 60)


class Application:
    """Example application using all toolkit modules."""

    def __init__(self, config_path: str = "configs/config.yaml"):
        # Load configuration
        self.config = ConfigManager.from_yaml(config_path)

        # Setup logging
        self.logger = LoggerFactory.from_yaml("configs/logging.yaml")

        # Setup environment
        self.env = EnvManager.from_yaml("configs/env.yaml")

        # Configure logger context
        self.logger.set_context(
            app_name=self.config.get("app.name"),
            environment=self.env.get_environment().value,
        )

        self.logger.info("Application initialized")

    def run(self):
        """Run the application."""
        self.logger.info("Application starting...")

        try:
            # Validate required environment variables
            self.env.validate_required()

            # Your application logic here
            self.logger.info("Application running", extra={"status": "healthy"})

        except ValidationError as e:
            self.logger.error(f"Validation error: {e.message}", extra=e.details)
        except ApplicationError as e:
            self.logger.error(
                f"Application error: {e.code} - {e.message}", extra=e.details
            )
        except Exception as e:
            self.logger.exception("Unexpected error occurred")
        finally:
            self.logger.info("Application shutdown")


# Run example application
if __name__ == "__main__":
    try:
        app = Application()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
