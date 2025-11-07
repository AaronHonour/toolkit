"""Factory pattern for test data generation."""

from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar("T")


class Factory:
    """
    Factory for generating test data.

    Examples:
        >>> class UserFactory(Factory):
        ...     model = User
        ...
        ...     @classmethod
        ...     def defaults(cls) -> Dict:
        ...         return {
        ...             "name": "Test User",
        ...             "email": f"user{cls.sequence()}@example.com",
        ...             "is_active": True,
        ...         }
        >>>
        >>> user = UserFactory.create()
        >>> users = UserFactory.create_batch(10)
    """

    model: Type = None
    _sequence = 0

    @classmethod
    def defaults(cls) -> Dict[str, Any]:
        """
        Default attributes for factory.

        Override this method to provide default values.
        """
        return {}

    @classmethod
    def create(cls, **kwargs) -> Any:
        """
        Create a single instance.

        Args:
            **kwargs: Override default attributes

        Returns:
            Model instance
        """
        attrs = cls.defaults()
        attrs.update(kwargs)

        if cls.model:
            return cls.model(**attrs)
        return attrs

    @classmethod
    def create_batch(cls, count: int, **kwargs) -> list:
        """
        Create multiple instances.

        Args:
            count: Number of instances to create
            **kwargs: Override default attributes

        Returns:
            List of model instances
        """
        return [cls.create(**kwargs) for _ in range(count)]

    @classmethod
    def sequence(cls) -> int:
        """
        Get next sequence number.

        Returns:
            Sequence number
        """
        cls._sequence += 1
        return cls._sequence
