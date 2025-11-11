"""Tests for error base classes."""

import pytest

from unistax.errors import (
    ApplicationError,
    ErrorCode,
    ErrorCategory,
    ValidationError,
    DatabaseError,
    NotFoundError,
)


class TestApplicationError:
    """Test ApplicationError class."""

    def test_basic_error(self):
        """Test creating basic error."""
        error = ApplicationError("Test error")
        assert error.message == "Test error"
        assert error.code == ErrorCode.INTERNAL_ERROR
        assert error.category == ErrorCategory.INTERNAL
        assert error.details == {}
        assert error.cause is None

    def test_error_with_code(self):
        """Test error with custom code."""
        error = ApplicationError("Test error", code=ErrorCode.VALIDATION_FAILED)
        assert error.code == ErrorCode.VALIDATION_FAILED

    def test_error_with_details(self):
        """Test error with details."""
        details = {"field": "email", "value": "invalid"}
        error = ApplicationError("Test error", details=details)
        assert error.details == details

    def test_error_with_cause(self):
        """Test error with cause."""
        cause = ValueError("Original error")
        error = ApplicationError("Test error", cause=cause)
        assert error.cause == cause

    def test_error_to_dict(self):
        """Test error serialization to dict."""
        error = ApplicationError(
            "Test error",
            code=ErrorCode.VALIDATION_FAILED,
            details={"field": "email"},
        )
        error_dict = error.to_dict()

        assert error_dict["error"] == "ApplicationError"
        assert error_dict["code"] == ErrorCode.VALIDATION_FAILED.value
        assert error_dict["message"] == "Test error"
        assert error_dict["details"] == {"field": "email"}

    def test_error_str(self):
        """Test error string representation."""
        error = ApplicationError("Test error", details={"key": "value"})
        error_str = str(error)
        assert "[INTERNAL_9001]" in error_str
        assert "Test error" in error_str
        assert "Details:" in error_str

    def test_error_repr(self):
        """Test error repr."""
        error = ApplicationError("Test error")
        error_repr = repr(error)
        assert "ApplicationError" in error_repr
        assert "INTERNAL_9001" in error_repr
        assert "Test error" in error_repr


class TestSpecificErrors:
    """Test specific error types."""

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid input")
        assert error.code == ErrorCode.VALIDATION_FAILED
        assert error.category == ErrorCategory.VALIDATION

    def test_database_error(self):
        """Test DatabaseError."""
        error = DatabaseError("Connection failed")
        assert error.code == ErrorCode.DATABASE_CONNECTION
        assert error.category == ErrorCategory.DATABASE

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("Resource not found")
        assert error.code == ErrorCode.RESOURCE_NOT_FOUND
        assert error.category == ErrorCategory.NOT_FOUND

    def test_error_inheritance(self):
        """Test error inheritance."""
        error = ValidationError("Test")
        assert isinstance(error, ApplicationError)
        assert isinstance(error, Exception)

    def test_custom_code_override(self):
        """Test overriding default error code."""
        error = ValidationError("Test", code=ErrorCode.MISSING_REQUIRED)
        assert error.code == ErrorCode.MISSING_REQUIRED
        # Category should still be from class
        assert error.category == ErrorCategory.VALIDATION
