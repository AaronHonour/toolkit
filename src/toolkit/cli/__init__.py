"""
CLI Module.

Provides CLI framework with:
- Command registration
- Argument parsing
- Code generation/scaffolding
"""

from .cli import CLI, command, option, argument
from .scaffold import Scaffolder

__all__ = ["CLI", "command", "option", "argument", "Scaffolder"]
