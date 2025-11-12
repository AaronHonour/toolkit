"""API route decorators."""

from collections.abc import Callable

# Re-export FastAPI route decorators for convenience


def get(path: str, **kwargs) -> Callable:
    """GET endpoint decorator."""

    def decorator(func: Callable) -> Callable:
        func._http_method = "GET"
        func._path = path
        func._kwargs = kwargs
        return func

    return decorator


def post(path: str, **kwargs) -> Callable:
    """POST endpoint decorator."""

    def decorator(func: Callable) -> Callable:
        func._http_method = "POST"
        func._path = path
        func._kwargs = kwargs
        return func

    return decorator


def put(path: str, **kwargs) -> Callable:
    """PUT endpoint decorator."""

    def decorator(func: Callable) -> Callable:
        func._http_method = "PUT"
        func._path = path
        func._kwargs = kwargs
        return func

    return decorator


def patch(path: str, **kwargs) -> Callable:
    """PATCH endpoint decorator."""

    def decorator(func: Callable) -> Callable:
        func._http_method = "PATCH"
        func._path = path
        func._kwargs = kwargs
        return func

    return decorator


def delete(path: str, **kwargs) -> Callable:
    """DELETE endpoint decorator."""

    def decorator(func: Callable) -> Callable:
        func._http_method = "DELETE"
        func._path = path
        func._kwargs = kwargs
        return func

    return decorator
