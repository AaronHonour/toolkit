"""Fallback pattern implementation."""

from collections.abc import Callable
from functools import wraps
from typing import Any


class Fallback:
    """Fallback pattern for graceful degradation.

    Examples:
        >>> fallback = Fallback(default_value={"status": "unavailable"})
        >>> @fallback.with_fallback()
        ... def get_user_data(user_id):
        ...     return api.get(f"/users/{user_id}")
    """

    def __init__(self, default_value: Any = None, fallback_func: Callable = None):
        """Initialize Fallback.

        Args:
            default_value: Default value to return on failure
            fallback_func: Fallback function to call on failure
        """
        self.default_value = default_value
        self.fallback_func = fallback_func

    def with_fallback(self, fallback_func: Callable = None):
        """Decorator to add fallback behavior.

        Args:
            fallback_func: Custom fallback function
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if fallback_func:
                        return fallback_func(*args, **kwargs)
                    elif self.fallback_func:
                        return self.fallback_func(*args, **kwargs)
                    return self.default_value

            return wrapper

        return decorator
