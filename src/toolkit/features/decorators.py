"""Feature flag decorators."""

from typing import Callable, Optional
from functools import wraps
from toolkit.features.manager import FeatureManager

_feature_manager: Optional[FeatureManager] = None


def set_feature_manager(manager: FeatureManager):
    """Set global feature manager."""
    global _feature_manager
    _feature_manager = manager


def is_enabled(feature_name: str, user_id: Optional[str] = None) -> bool:
    """Check if feature is enabled."""
    if not _feature_manager:
        return False
    return _feature_manager.is_enabled(feature_name, user_id=user_id)


def feature_flag(feature_name: str, fallback: Optional[Callable] = None):
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
