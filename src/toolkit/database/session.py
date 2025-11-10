"""Database session management."""

from typing import Generator, Optional
from contextlib import contextmanager
from contextvars import ContextVar
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from toolkit.database.connection import DatabaseManager

# Thread-local session storage
_session_context: ContextVar[Optional[Session]] = ContextVar("session", default=None)

# Global session factory
_session_factory: Optional[sessionmaker] = None
_scoped_session: Optional[scoped_session] = None


class SessionManager:
    """Manage database sessions."""

    def __init__(self, database_manager: DatabaseManager):
        """Initialize session manager.

        Args:
            database_manager: Database manager instance
        """
        self.database_manager = database_manager
        self._setup_session_factory()

    def _setup_session_factory(self):
        """Setup session factory."""
        global _session_factory, _scoped_session

        if _session_factory is None:
            _session_factory = self.database_manager.get_session_factory()
            _scoped_session = scoped_session(_session_factory)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Create a session context.

        Yields:
            Database session

        Example:
            with session_manager.session() as session:
                user = session.query(User).first()
        """
        session = _session_factory()

        # Set in context
        token = _session_context.set(session)

        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            _session_context.reset(token)

    def get_scoped_session(self) -> Session:
        """Get scoped session.

        Returns:
            Scoped database session
        """
        return _scoped_session()

    def remove_scoped_session(self):
        """Remove scoped session."""
        if _scoped_session:
            _scoped_session.remove()

    @staticmethod
    def get_current_session() -> Optional[Session]:
        """Get current session from context.

        Returns:
            Current session or None
        """
        return _session_context.get()


def get_session() -> Session:
    """Get current database session.

    Returns:
        Current session

    Raises:
        RuntimeError: If no session is active
    """
    session = _session_context.get()
    if session is None:
        raise RuntimeError("No active database session")
    return session


@contextmanager
def transaction() -> Generator[Session, None, None]:
    """Create a transaction context.

    Yields:
        Database session

    Example:
        with transaction() as session:
            user = User(name="John")
            session.add(user)
    """
    session = get_session()

    # Create savepoint for nested transactions
    nested = session.begin_nested()

    try:
        yield session
        nested.commit()
    except Exception:
        nested.rollback()
        raise
