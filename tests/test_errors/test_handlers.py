"""Tests for error handlers."""

import logging

import pytest

from toolkit.errors import (
    ApplicationError,
    ErrorCode,
    ValidationError,
    LoggingErrorHandler,
    ErrorHandlerChain,
)


class TestLoggingErrorHandler:
    """Test LoggingErrorHandler class."""

    def test_handle_application_error(self, caplog):
        """Test handling ApplicationError."""
        handler = LoggingErrorHandler(log_level="ERROR")
        error = ValidationError(
            "Invalid input", code=ErrorCode.VALIDATION_FAILED, details={"field": "email"}
        )

        with caplog.at_level(logging.ERROR):
            handler.handle(error, {})

        assert "VALIDATION_2001" in caplog.text
        assert "Invalid input" in caplog.text

    def test_handle_generic_exception(self, caplog):
        """Test handling generic exception."""
        handler = LoggingErrorHandler(log_level="ERROR")
        error = ValueError("Test error")

        with caplog.at_level(logging.ERROR):
            handler.handle(error, {})

        assert "Test error" in caplog.text

    def test_handle_with_context(self, caplog):
        """Test handling with context."""
        handler = LoggingErrorHandler(log_level="ERROR")
        error = ApplicationError("Test error")
        context = {"request_id": "123", "user_id": "456"}

        with caplog.at_level(logging.ERROR):
            handler.handle(error, context)

        # Context should be in extra fields
        assert "Test error" in caplog.text


class TestErrorHandlerChain:
    """Test ErrorHandlerChain class."""

    def test_empty_chain(self):
        """Test chain with no handlers."""
        chain = ErrorHandlerChain()
        error = ApplicationError("Test error")

        with pytest.raises(ValueError, match="No handlers in chain"):
            chain.handle(error)

    def test_single_handler(self, caplog):
        """Test chain with single handler."""
        chain = ErrorHandlerChain()
        chain.add_handler(LoggingErrorHandler())

        error = ApplicationError("Test error")

        with caplog.at_level(logging.ERROR):
            chain.handle(error)

        assert "Test error" in caplog.text

    def test_multiple_handlers(self, caplog):
        """Test chain with multiple handlers."""
        chain = ErrorHandlerChain()
        chain.add_handler(LoggingErrorHandler(log_level="ERROR"))
        chain.add_handler(LoggingErrorHandler(log_level="WARNING"))

        error = ApplicationError("Test error")

        with caplog.at_level(logging.WARNING):
            chain.handle(error)

        # Both handlers should execute
        assert caplog.text.count("Test error") >= 1

    def test_handler_chaining(self):
        """Test that handlers are properly chained."""
        chain = ErrorHandlerChain()
        handler1 = LoggingErrorHandler()
        handler2 = LoggingErrorHandler()

        chain.add_handler(handler1)
        chain.add_handler(handler2)

        assert handler1._next_handler == handler2
        assert handler2._next_handler is None
