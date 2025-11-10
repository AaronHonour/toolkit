"""Decorators for dependency injection."""

from functools import wraps
from typing import Type, TypeVar

from .container import Lifetime

T = TypeVar("T")


def singleton(cls: Type[T]) -> Type[T]:
    """
    Mark a class as singleton.

    Example:
        >>> @singleton
        ... class UserService:
        ...     pass
    """
    cls.__lifetime__ = Lifetime.SINGLETON
    return cls


def transient(cls: Type[T]) -> Type[T]:
    """
    Mark a class as transient (new instance each time).

    Example:
        >>> @transient
        ... class RequestHandler:
        ...     pass
    """
    cls.__lifetime__ = Lifetime.TRANSIENT
    return cls


def scoped(cls: Type[T]) -> Type[T]:
    """
    Mark a class as scoped (one instance per scope).

    Example:
        >>> @scoped
        ... class DatabaseContext:
        ...     pass
    """
    cls.__lifetime__ = Lifetime.SCOPED
    return cls
