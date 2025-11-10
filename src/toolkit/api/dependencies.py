"""API dependency injection helpers."""

from typing import Any, Callable
from fastapi import Depends as FastAPIDepends


# Re-export FastAPI Depends
Depends = FastAPIDepends


def inject(dependency: Callable) -> Any:
    """Inject dependency into endpoint.

    Args:
        dependency: Dependency provider function

    Returns:
        Depends instance
    """
    return Depends(dependency)
