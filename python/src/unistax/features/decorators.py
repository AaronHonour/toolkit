"""Feature flag decorators."""

from collections.abc import Callable
from functools import wraps

from unistax.features.manager import FeatureManager

_feature_manager: FeatureManager | None = None


def set_feature_manager(manager: FeatureManager):
    """Set global feature manager."""
    global _feature_manager
    _feature_manager = manager


def is_enabled(feature_name: str, user_id: str | None = None) -> bool:
    """Check if feature is enabled."""
    if not _feature_manager:
        return False
    return _feature_manager.is_enabled(feature_name, user_id=user_id)


def feature_flag(feature_name: str, fallback: Callable | None = None):
    """Decorator to check feature flag before executing function."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if is_enabled(feature_name):
                return func(*args, **kwargs)
            elif fallback:
                return fallback(*args, **kwargs)
            else:
                raise RuntimeError(f"Feature '{feature_name}' is not enabled")

        return wrapper

    return decorator
