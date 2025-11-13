"""Database migration management using Alembic."""

import os
from pathlib import Path

from alembic import command  # type: ignore[import-not-found]
from alembic.config import Config  # type: ignore[import-not-found]

from unistax.database.connection import DatabaseManager


class MigrationManager:
    """Manage database migrations with Alembic."""

    def __init__(
        self,
        database_manager: DatabaseManager,
        migrations_dir: str = "migrations",
        script_location: str | None = None,
    ) -> None:
        """Initialize migration manager.

        Args:
            database_manager: Database manager instance
            migrations_dir: Directory for migration files
            script_location: Alembic script location
        """
        self.database_manager = database_manager
        self.migrations_dir = migrations_dir
        self.script_location = script_location or migrations_dir

    def _get_alembic_config(self) -> Config:
        """Get Alembic configuration.

        Returns:
            Alembic config object
        """
        # Create migrations directory if it doesn't exist
        Path(self.migrations_dir).mkdir(parents=True, exist_ok=True)

        # Create alembic.ini if it doesn't exist
        alembic_ini = os.path.join(self.migrations_dir, "alembic.ini")
        if not os.path.exists(alembic_ini):
            self._create_alembic_ini(alembic_ini)

        config = Config(alembic_ini)
        config.set_main_option("script_location", self.script_location)
        config.set_main_option("sqlalchemy.url", self.database_manager.config.url)

        return config

    def _create_alembic_ini(self, path: str) -> None:
        """Create default alembic.ini file.

        Args:
            path: Path to alembic.ini
        """
        content = """# A generic, single database configuration.

[alembic]
script_location = %(script_location)s
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        with open(path, "w") as f:
            f.write(content)

    def init(self) -> None:
        """Initialize Alembic in the migrations directory."""
        config = self._get_alembic_config()
        command.init(config, self.script_location)

    def revision(
        self,
        message: str,
        autogenerate: bool = False,
        sql: bool = False,
        head: str = "head",
    ) -> None:
        """Create a new migration revision.

        Args:
            message: Revision message
            autogenerate: Auto-generate migration from models
            sql: Generate SQL instead of Python
            head: Head revision
        """
        config = self._get_alembic_config()
        command.revision(
            config,
            message=message,
            autogenerate=autogenerate,
            sql=sql,
            head=head,
        )

    def upgrade(self, revision: str = "head") -> None:
        """Upgrade to a specific revision.

        Args:
            revision: Target revision (default: head)
        """
        config = self._get_alembic_config()
        command.upgrade(config, revision)

    def downgrade(self, revision: str) -> None:
        """Downgrade to a specific revision.

        Args:
            revision: Target revision
        """
        config = self._get_alembic_config()
        command.downgrade(config, revision)

    def current(self) -> None:
        """Display current revision."""
        config = self._get_alembic_config()
        command.current(config)

    def history(self, verbose: bool = False) -> None:
        """Display migration history.

        Args:
            verbose: Show verbose output
        """
        config = self._get_alembic_config()
        command.history(config, verbose=verbose)

    def stamp(self, revision: str) -> None:
        """Stamp database with a specific revision.

        Args:
            revision: Revision to stamp
        """
        config = self._get_alembic_config()
        command.stamp(config, revision)

    def merge(self, revisions: str, message: str | None = None) -> None:
        """Merge multiple revisions.

        Args:
            revisions: Revisions to merge
            message: Merge message
        """
        config = self._get_alembic_config()
        command.merge(config, revisions=revisions, message=message)
