"""Error handlers for processing and responding to errors.

Provides composable error handling strategies.
"""

from abc import ABC, abstractmethod
from typing import Any

from .base import ApplicationError


class ErrorHandler(ABC):
    """Abstract base class for error handlers.

    Error handlers can be chained using the Chain of Responsibility pattern.
    """

    def __init__(self) -> None:
        """Initialize error handler."""
        self._next_handler: ErrorHandler | None = None

    def set_next(self, handler: "ErrorHandler") -> "ErrorHandler":
        """Set next handler in chain.

        Args:
            handler: Next error handler

        Returns:
            The handler that was set (for chaining)
        """
        self._next_handler = handler
        return handler

    def handle(self, error: Exception, context: dict[str, Any] | None = None) -> Any:
        """Handle error and optionally pass to next handler.

        Args:
            error: Exception to handle
            context: Additional context

        Returns:
            Handler result
        """
        result = self._handle_error(error, context or {})

        if self._next_handler:
            return self._next_handler.handle(error, context)

        return result

    @abstractmethod
    def _handle_error(self, error: Exception, context: dict[str, Any]) -> Any:
        """Implement error handling logic.

        Args:
            error: Exception to handle
            context: Additional context

        Returns:
            Handler result
        """
        pass


class LoggingErrorHandler(ErrorHandler):
    """Error handler that logs errors.

    Integrates with the logging module for consistent error logging.
    """

    def __init__(
        self,
        logger: Any | None = None,
        log_level: str = "ERROR",
        include_traceback: bool = True,
    ) -> None:
        """Initialize logging error handler.

        Args:
            logger: Logger instance (uses root logger if None)
            log_level: Log level for errors
            include_traceback: Whether to include traceback
        """
        super().__init__()
        self._logger = logger
        self._log_level = log_level
        self._include_traceback = include_traceback

    def _handle_error(self, error: Exception, context: dict[str, Any]) -> None:
        """Log the error with context."""
        import logging

        logger = self._logger or logging.getLogger(__name__)

        # Prepare log message
        if isinstance(error, ApplicationError):
            message = f"[{error.code.value}] {error.message}"
            extra = {
                "error_code": error.code.value,
                "error_category": error.category.value,
                "error_details": error.details,
                **context,
            }
        else:
            message = str(error)
            extra = {"error_type": type(error).__name__, **context}

        # Log with appropriate level
        log_func = getattr(logger, self._log_level.lower(), logger.error)

        if self._include_traceback:
            log_func(message, exc_info=True, extra=extra)
        else:
            log_func(message, extra=extra)


class RetryErrorHandler(ErrorHandler):
    """Error handler that retries failed operations.

    Useful for transient errors (network, database connection, etc.)
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_on: list[type[Exception]] | None = None,
        backoff_factor: float = 2.0,
    ) -> None:
        """Initialize retry error handler.

        Args:
            max_retries: Maximum number of retry attempts
            retry_on: Exception types to retry on (None = all)
            backoff_factor: Exponential backoff multiplier
        """
        super().__init__()
        self._max_retries = max_retries
        self._retry_on = retry_on
        self._backoff_factor = backoff_factor

    def _handle_error(self, error: Exception, context: dict[str, Any]) -> None:
        """Determine if error should be retried."""
        if self._should_retry(error):
            retry_count = context.get("retry_count", 0)
            if retry_count < self._max_retries:
                context["should_retry"] = True
                context["retry_count"] = retry_count + 1
                context["backoff_delay"] = self._backoff_factor**retry_count

    def _should_retry(self, error: Exception) -> bool:
        """Check if error should be retried."""
        if self._retry_on is None:
            return True
        return any(isinstance(error, exc_type) for exc_type in self._retry_on)


class ErrorHandlerChain:
    """Manages a chain of error handlers.

    Provides a convenient way to build and execute handler chains.
    """

    def __init__(self) -> None:
        """Initialize error handler chain."""
        self._handlers: list[ErrorHandler] = []

    def add_handler(self, handler: ErrorHandler) -> "ErrorHandlerChain":
        """Add handler to chain.

        Args:
            handler: Error handler to add

        Returns:
            Self for method chaining
        """
        if self._handlers:
            self._handlers[-1].set_next(handler)
        self._handlers.append(handler)
        return self

    def handle(self, error: Exception, context: dict[str, Any] | None = None) -> Any:
        """Execute handler chain.

        Args:
            error: Exception to handle
            context: Additional context

        Returns:
            Result from first handler
        """
        if not self._handlers:
            raise ValueError("No handlers in chain")

        return self._handlers[0].handle(error, context or {})

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "ErrorHandlerChain":
        """Create handler chain from configuration.

        Args:
            config: Handler configuration

        Returns:
            Configured handler chain
        """
        chain = cls()

        for handler_config in config.get("handlers", []):
            handler_type = handler_config.get("type")

            if handler_type == "logging":
                handler = LoggingErrorHandler(
                    log_level=handler_config.get("level", "ERROR"),
                    include_traceback=handler_config.get("traceback", True),
                )
            elif handler_type == "retry":
                handler = RetryErrorHandler(
                    max_retries=handler_config.get("max_retries", 3),
                    backoff_factor=handler_config.get("backoff_factor", 2.0),
                )
            else:
                continue

            chain.add_handler(handler)

        return chain
