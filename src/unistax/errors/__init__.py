"""
Error Handling Module.

Provides a comprehensive error handling system with:
- Typed exception hierarchy
- Error codes and categorization
- Context preservation
- Error handlers
"""

from .base import (
    ApplicationError,
    ErrorCode,
    ErrorCategory,
    ConfigurationError,
    ValidationError,
    DatabaseError,
    NetworkError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
)
from .handlers import ErrorHandler, LoggingErrorHandler, ErrorHandlerChain
from .registry import ErrorRegistry

__all__ = [
    # Base classes
    "ApplicationError",
    "ErrorCode",
    "ErrorCategory",
    # Specific errors
    "ConfigurationError",
    "ValidationError",
    "DatabaseError",
    "NetworkError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    # Handlers
    "ErrorHandler",
    "LoggingErrorHandler",
    "ErrorHandlerChain",
    # Registry
    "ErrorRegistry",
]
