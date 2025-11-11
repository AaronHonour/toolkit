"""
Dependency Injection Module.

Provides a comprehensive DI container with:
- Auto-wiring based on type hints
- Lifetime management (singleton, transient, scoped)
- Factory registration
- Circular dependency detection
- Configuration binding
"""

from .container import Container, injectable, inject, Lifetime
from .decorators import singleton, transient, scoped
from .exceptions import DependencyResolutionError, CircularDependencyError

__all__ = [
    "Container",
    "injectable",
    "inject",
    "Lifetime",
    "singleton",
    "transient",
    "scoped",
    "DependencyResolutionError",
    "CircularDependencyError",
]
