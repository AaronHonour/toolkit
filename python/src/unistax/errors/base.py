"""
Base exception classes and error codes.

Provides a typed exception hierarchy with error codes, categories,
and context preservation.
"""

from enum import Enum
from typing import Any


class ErrorCategory(str, Enum):
    """Error category enumeration."""

    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    DATABASE = "database"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    INTERNAL = "internal"
    EXTERNAL = "external"


class ErrorCode(str, Enum):
    """
    Standardized error codes.

    Follow pattern: CATEGORY_SPECIFIC_ERROR
    """

    # Configuration errors (1xxx)
    CONFIG_MISSING = "CONFIG_1001"
    CONFIG_INVALID = "CONFIG_1002"
    CONFIG_LOAD_FAILED = "CONFIG_1003"

    # Validation errors (2xxx)
    VALIDATION_FAILED = "VALIDATION_2001"
    INVALID_INPUT = "VALIDATION_2002"
    INVALID_FORMAT = "VALIDATION_2003"
    MISSING_REQUIRED = "VALIDATION_2004"

    # Database errors (3xxx)
    DATABASE_CONNECTION = "DATABASE_3001"
    DATABASE_QUERY = "DATABASE_3002"
    DATABASE_TRANSACTION = "DATABASE_3003"
    DATABASE_CONSTRAINT = "DATABASE_3004"

    # Network errors (4xxx)
    NETWORK_TIMEOUT = "NETWORK_4001"
    NETWORK_CONNECTION = "NETWORK_4002"
    NETWORK_DNS = "NETWORK_4003"

    # Authentication errors (5xxx)
    AUTH_INVALID_CREDENTIALS = "AUTH_5001"
    AUTH_TOKEN_EXPIRED = "AUTH_5002"
    AUTH_TOKEN_INVALID = "AUTH_5003"
    AUTH_REQUIRED = "AUTH_5004"

    # Authorization errors (6xxx)
    AUTHZ_FORBIDDEN = "AUTHZ_6001"
    AUTHZ_INSUFFICIENT_PERMISSIONS = "AUTHZ_6002"

    # Resource errors (7xxx)
    RESOURCE_NOT_FOUND = "RESOURCE_7001"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_7002"
    RESOURCE_CONFLICT = "RESOURCE_7003"

    # Rate limiting (8xxx)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_8001"

    # Internal errors (9xxx)
    INTERNAL_ERROR = "INTERNAL_9001"
    NOT_IMPLEMENTED = "INTERNAL_9002"


class ApplicationError(Exception):
    """
    Base application error with enhanced context.

    Attributes:
        code: Error code for identification
        message: Human-readable error message
        category: Error category
        details: Additional context (e.g., field names, values)
        cause: Original exception if wrapping another error
    """

    code: ErrorCode = ErrorCode.INTERNAL_ERROR
    category: ErrorCategory = ErrorCategory.INTERNAL

    def __init__(
        self,
        message: str,
        code: ErrorCode | None = None,
        category: ErrorCategory | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Initialize application error.

        Args:
            message: Error message
            code: Error code (overrides class default)
            category: Error category (overrides class default)
            details: Additional context dictionary
            cause: Original exception
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.code
        self.category = category or self.__class__.category
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """
        Convert error to dictionary for serialization.

        Returns:
            Dictionary representation of error
        """
        result: dict[str, Any] = {
            "error": self.__class__.__name__,
            "code": self.code.value,
            "category": self.category.value,
            "message": self.message,
        }

        if self.details:
            result["details"] = self.details

        if self.cause:
            result["cause"] = str(self.cause)

        return result

    def __str__(self) -> str:
        """String representation of error."""
        parts = [f"[{self.code.value}] {self.message}"]
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Developer representation of error."""
        return (
            f"{self.__class__.__name__}("
            f"code={self.code.value}, "
            f"message={self.message!r}, "
            f"details={self.details})"
        )


# Specific error types


class ConfigurationError(ApplicationError):
    """Configuration-related errors."""

    code = ErrorCode.CONFIG_INVALID
    category = ErrorCategory.CONFIGURATION


class ValidationError(ApplicationError):
    """Validation errors."""

    code = ErrorCode.VALIDATION_FAILED
    category = ErrorCategory.VALIDATION


class DatabaseError(ApplicationError):
    """Database-related errors."""

    code = ErrorCode.DATABASE_CONNECTION
    category = ErrorCategory.DATABASE


class NetworkError(ApplicationError):
    """Network-related errors."""

    code = ErrorCode.NETWORK_CONNECTION
    category = ErrorCategory.NETWORK


class AuthenticationError(ApplicationError):
    """Authentication errors."""

    code = ErrorCode.AUTH_INVALID_CREDENTIALS
    category = ErrorCategory.AUTHENTICATION


class AuthorizationError(ApplicationError):
    """Authorization errors."""

    code = ErrorCode.AUTHZ_FORBIDDEN
    category = ErrorCategory.AUTHORIZATION


class NotFoundError(ApplicationError):
    """Resource not found errors."""

    code = ErrorCode.RESOURCE_NOT_FOUND
    category = ErrorCategory.NOT_FOUND


class ConflictError(ApplicationError):
    """Resource conflict errors."""

    code = ErrorCode.RESOURCE_CONFLICT
    category = ErrorCategory.CONFLICT


class RateLimitError(ApplicationError):
    """Rate limiting errors."""

    code = ErrorCode.RATE_LIMIT_EXCEEDED
    category = ErrorCategory.RATE_LIMIT
