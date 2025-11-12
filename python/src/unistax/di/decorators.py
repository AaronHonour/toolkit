"""Decorators for dependency injection."""

from typing import TypeVar

from .container import Lifetime

T = TypeVar("T")


def singleton(cls: type[T]) -> type[T]:
    """Mark a class as singleton.

    Example:
        >>> @singleton
        ... class UserService:
        ...     pass
    """
    cls.__lifetime__ = Lifetime.SINGLETON
    return cls


def transient(cls: type[T]) -> type[T]:
    """Mark a class as transient (new instance each time).

    Example:
        >>> @transient
        ... class RequestHandler:
        ...     pass
    """
    cls.__lifetime__ = Lifetime.TRANSIENT
    return cls


def scoped(cls: type[T]) -> type[T]:
    """Mark a class as scoped (one instance per scope).

    Example:
        >>> @scoped
        ... class DatabaseContext:
        ...     pass
    """
    cls.__lifetime__ = Lifetime.SCOPED
    return cls
