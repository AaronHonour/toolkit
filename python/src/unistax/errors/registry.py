"""Error registry for tracking and categorizing errors.

Provides utilities for error management and reporting.
"""

from collections import defaultdict

from .base import ApplicationError, ErrorCategory, ErrorCode


class ErrorRegistry:
    """Registry for tracking error types and occurrences.

    Useful for monitoring and debugging.
    """

    def __init__(self) -> None:
        """Initialize error registry."""
        self._errors: dict[ErrorCode, type[ApplicationError]] = {}
        self._occurrences: dict[ErrorCode, int] = defaultdict(int)

    def register(self, error_class: type[ApplicationError]) -> None:
        """Register error class.

        Args:
            error_class: Error class to register
        """
        self._errors[error_class.code] = error_class

    def record_occurrence(self, error: ApplicationError) -> None:
        """Record error occurrence.

        Args:
            error: Error instance
        """
        self._occurrences[error.code] += 1

    def get_error_class(self, code: ErrorCode) -> type[ApplicationError]:
        """Get error class by code.

        Args:
            code: Error code

        Returns:
            Error class

        Raises:
            KeyError: If code not registered
        """
        return self._errors[code]

    def get_occurrences(self, code: ErrorCode) -> int:
        """Get occurrence count for error code.

        Args:
            code: Error code

        Returns:
            Occurrence count
        """
        return self._occurrences[code]

    def get_errors_by_category(self, category: ErrorCategory) -> list[type[ApplicationError]]:
        """Get all errors in a category.

        Args:
            category: Error category

        Returns:
            List of error classes
        """
        return [
            error_class for error_class in self._errors.values() if error_class.category == category
        ]

    def get_statistics(self) -> dict[str, int]:
        """Get error statistics.

        Returns:
            Dictionary mapping error codes to counts
        """
        return {code.value: count for code, count in self._occurrences.items()}

    def reset_statistics(self) -> None:
        """Reset occurrence statistics."""
        self._occurrences.clear()


# Global registry instance
_global_registry = ErrorRegistry()


def get_global_registry() -> ErrorRegistry:
    """Get global error registry instance."""
    return _global_registry
