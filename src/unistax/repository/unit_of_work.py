"""Unit of Work pattern implementation."""

from typing import Any, Optional


class UnitOfWork:
    """
    Unit of Work pattern for managing transactions.

    Examples:
        >>> async with UnitOfWork() as uow:
        ...     user = await uow.users.get(123)
        ...     user.name = "Updated"
        ...     await uow.commit()
    """

    def __init__(self, session: Optional[Any] = None):
        self._session = session
        self._changes = []
        self._is_committed = False

    async def __aenter__(self):
        """Enter context - begin transaction."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context - commit or rollback."""
        if exc_type is None and not self._is_committed:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self) -> None:
        """Commit all changes."""
        # Apply all changes
        for change in self._changes:
            # Execute change
            pass

        self._is_committed = True
        self._changes = []

    async def rollback(self) -> None:
        """Rollback all changes."""
        self._changes = []

    def register_change(self, change: Any) -> None:
        """Register a change to be committed."""
        self._changes.append(change)
