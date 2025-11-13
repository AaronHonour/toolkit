"""API route decorators."""

from collections.abc import Callable
from typing import Any

# Re-export FastAPI route decorators for convenience


def get(path: str, **kwargs: Any) -> Callable[..., Any]:
    """GET endpoint decorator."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._http_method = "GET"  # type: ignore[attr-defined]
        func._path = path  # type: ignore[attr-defined]
        func._kwargs = kwargs  # type: ignore[attr-defined]
        return func

    return decorator


def post(path: str, **kwargs: Any) -> Callable[..., Any]:
    """POST endpoint decorator."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._http_method = "POST"  # type: ignore[attr-defined]
        func._path = path  # type: ignore[attr-defined]
        func._kwargs = kwargs  # type: ignore[attr-defined]
        return func

    return decorator


def put(path: str, **kwargs: Any) -> Callable[..., Any]:
    """PUT endpoint decorator."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._http_method = "PUT"  # type: ignore[attr-defined]
        func._path = path  # type: ignore[attr-defined]
        func._kwargs = kwargs  # type: ignore[attr-defined]
        return func

    return decorator


def patch(path: str, **kwargs: Any) -> Callable[..., Any]:
    """PATCH endpoint decorator."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._http_method = "PATCH"  # type: ignore[attr-defined]
        func._path = path  # type: ignore[attr-defined]
        func._kwargs = kwargs  # type: ignore[attr-defined]
        return func

    return decorator


def delete(path: str, **kwargs: Any) -> Callable[..., Any]:
    """DELETE endpoint decorator."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._http_method = "DELETE"  # type: ignore[attr-defined]
        func._path = path  # type: ignore[attr-defined]
        func._kwargs = kwargs  # type: ignore[attr-defined]
        return func

    return decorator
