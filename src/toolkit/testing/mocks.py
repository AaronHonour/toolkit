"""Service mocking utilities."""

from typing import Any, Callable, Type
from unittest.mock import Mock


class MockService:
    """
    Mock service for testing.

    Examples:
        >>> mock_email = MockService()
        >>> mock_email.send = Mock(return_value=True)
        >>> mock_email.send("test@example.com")
        True
    """

    def __init__(self):
        self._mock = Mock()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._mock, name)


def mock_service(service_type: Type) -> Callable:
    """
    Decorator to mock a service in tests.

    Args:
        service_type: Service class to mock

    Returns:
        Decorator function

    Examples:
        >>> @mock_service(EmailService)
        ... async def test_send_email(email_service):
        ...     email_service.send = Mock(return_value=True)
        ...     result = await user_service.notify_user(123)
        ...     email_service.send.assert_called_once()
    """

    def decorator(func: Callable) -> Callable:
        from functools import wraps

        @wraps(func)
        async def wrapper(*args, **kwargs):
            mock = MockService()
            kwargs[service_type.__name__.lower().replace("service", "")] = mock
            return await func(*args, **kwargs)

        return wrapper

    return decorator
