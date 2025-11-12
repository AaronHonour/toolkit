"""Testing fixtures and utilities."""

from collections.abc import Callable


class TestCase:
    """
    Base test case class.

    Provides common test utilities and fixtures.

    Examples:
        >>> class TestUserService(TestCase):
        ...     async def test_create_user(self):
        ...         user = await self.services.user.create(email="test@example.com")
        ...         assert user.id is not None
    """

    def setup_method(self):
        """Setup method called before each test."""
        pass

    def teardown_method(self):
        """Teardown method called after each test."""
        pass


def fixture(func: Callable) -> Callable:
    """
    Mark function as a test fixture.

    Args:
        func: Fixture function

    Returns:
        Decorated function
    """
    func.__test_fixture__ = True
    return func


def use_test_db(func: Callable) -> Callable:
    """
    Decorator to use test database.

    Sets up and tears down test database for test.

    Args:
        func: Test function

    Returns:
        Decorated function
    """
    from functools import wraps

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Setup test database
        print("Setting up test database...")

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            # Teardown test database
            print("Tearing down test database...")

    return wrapper
