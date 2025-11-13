"""API dependency injection helpers."""

from collections.abc import Callable
from typing import Any

from fastapi import Depends as FastAPIDepends  # type: ignore[import-not-found]

# Re-export FastAPI Depends
Depends = FastAPIDepends


def inject(dependency: Callable[..., Any]) -> Any:
    """Inject dependency into endpoint.

    Args:
        dependency: Dependency provider function

    Returns:
        Depends instance
    """
    return Depends(dependency)
