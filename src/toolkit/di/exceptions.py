"""Exceptions for dependency injection."""


class DependencyResolutionError(Exception):
    """Raised when a dependency cannot be resolved."""

    pass


class CircularDependencyError(DependencyResolutionError):
    """Raised when a circular dependency is detected."""

    pass
