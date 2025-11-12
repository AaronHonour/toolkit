"""CLI framework implementation."""

import sys
from collections.abc import Callable
from typing import Any


class Command:
    """CLI command definition."""

    def __init__(self, name: str, func: Callable, description: str = ""):
        """Initialize Command.

        Args:
            name: Command name
            func: Command function
            description: Command description
        """
        self.name = name
        self.func = func
        self.description = description
        self.options: dict[str, Any] = {}
        self.arguments: list[str] = []


class CLI:
    """CLI framework for building command-line tools.

    Examples:
        >>> cli = CLI("toolkit")
        >>>
        >>> @cli.command()
        >>> @cli.option("--name", required=True)
        >>> def create(name: str):
        ...     print(f"Creating {name}")
        >>>
        >>> cli.run()
    """

    def __init__(self, name: str = "cli"):
        """Initialize CLI.

        Args:
            name: CLI application name
        """
        self.name = name
        self._commands: dict[str, Command] = {}

    def command(self, name: str | None = None, description: str = ""):
        """Register a command.

        Args:
            name: Command name (defaults to function name)
            description: Command description

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            cmd_name = name or func.__name__
            cmd = Command(cmd_name, func, description or func.__doc__ or "")
            self._commands[cmd_name] = cmd

            # Store command on function for options/arguments
            func.__cli_command__ = cmd
            return func

        return decorator

    def run(self, args: list[str] | None = None) -> None:
        """Run CLI with arguments.

        Args:
            args: Command-line arguments (defaults to sys.argv)
        """
        if args is None:
            args = sys.argv[1:]

        if not args or args[0] in ["-h", "--help"]:
            self._print_help()
            return

        cmd_name = args[0]
        if cmd_name not in self._commands:
            print(f"Error: Unknown command '{cmd_name}'")
            self._print_help()
            return

        command = self._commands[cmd_name]
        cmd_args = args[1:]

        # Parse options and arguments
        try:
            kwargs = self._parse_args(command, cmd_args)
            command.func(**kwargs)
        except Exception as e:
            print(f"Error: {e}")

    def _parse_args(self, command: Command, args: list[str]) -> dict[str, Any]:
        """Parse command arguments."""
        kwargs = {}
        i = 0

        while i < len(args):
            arg = args[i]

            if arg.startswith("--"):
                # Long option
                option_name = arg[2:]
                if i + 1 < len(args):
                    kwargs[option_name] = args[i + 1]
                    i += 2
                else:
                    kwargs[option_name] = True
                    i += 1
            elif arg.startswith("-"):
                # Short option
                option_name = arg[1:]
                if i + 1 < len(args):
                    kwargs[option_name] = args[i + 1]
                    i += 2
                else:
                    kwargs[option_name] = True
                    i += 1
            else:
                # Positional argument
                kwargs[f"arg{i}"] = arg
                i += 1

        return kwargs

    def _print_help(self) -> None:
        """Print help message."""
        print(f"Usage: {self.name} <command> [options]")
        print("\nCommands:")
        for name, cmd in self._commands.items():
            desc = cmd.description or "No description"
            print(f"  {name:<20} {desc}")


def command(name: str | None = None):
    """Decorator for defining a command."""

    def decorator(func: Callable) -> Callable:
        return func

    return decorator


def option(name: str, required: bool = False, default: Any = None):
    """Decorator for defining a command option."""

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "__cli_options__"):
            func.__cli_options__ = {}
        func.__cli_options__[name] = {"required": required, "default": default}
        return func

    return decorator


def argument(name: str):
    """Decorator for defining a command argument."""

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "__cli_arguments__"):
            func.__cli_arguments__ = []
        func.__cli_arguments__.append(name)
        return func

    return decorator
