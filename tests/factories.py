"""Test data factories for generating test data."""

import random
import string
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from datetime import datetime, timedelta
from dataclasses import dataclass, field

T = TypeVar("T")


class Factory:
    """Base factory for creating test objects."""

    _sequence = 0

    @classmethod
    def sequence(cls) -> int:
        """Get next sequence number."""
        cls._sequence += 1
        return cls._sequence

    @classmethod
    def reset_sequence(cls):
        """Reset sequence counter."""
        cls._sequence = 0


class StringFactory(Factory):
    """Generate random strings."""

    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate random string."""
        return "".join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def random_email() -> str:
        """Generate random email."""
        username = StringFactory.random_string(8).lower()
        domain = StringFactory.random_string(6).lower()
        return f"{username}@{domain}.com"

    @staticmethod
    def random_url() -> str:
        """Generate random URL."""
        domain = StringFactory.random_string(8).lower()
        return f"https://{domain}.com"

    @staticmethod
    def random_uuid() -> str:
        """Generate random UUID."""
        import uuid
        return str(uuid.uuid4())


class NumberFactory(Factory):
    """Generate random numbers."""

    @staticmethod
    def random_int(min_val: int = 0, max_val: int = 1000) -> int:
        """Generate random integer."""
        return random.randint(min_val, max_val)

    @staticmethod
    def random_float(min_val: float = 0.0, max_val: float = 1000.0) -> float:
        """Generate random float."""
        return random.uniform(min_val, max_val)

    @staticmethod
    def random_bool() -> bool:
        """Generate random boolean."""
        return random.choice([True, False])


class DateFactory(Factory):
    """Generate random dates."""

    @staticmethod
    def random_datetime(
        start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> datetime:
        """Generate random datetime."""
        if start is None:
            start = datetime.now() - timedelta(days=365)
        if end is None:
            end = datetime.now()

        delta = end - start
        random_seconds = random.randint(0, int(delta.total_seconds()))
        return start + timedelta(seconds=random_seconds)

    @staticmethod
    def future_datetime(days: int = 30) -> datetime:
        """Generate future datetime."""
        return datetime.now() + timedelta(days=random.randint(1, days))

    @staticmethod
    def past_datetime(days: int = 30) -> datetime:
        """Generate past datetime."""
        return datetime.now() - timedelta(days=random.randint(1, days))


class DataFactory(Factory):
    """Generate complex test data structures."""

    @staticmethod
    def random_dict(size: int = 5) -> Dict[str, Any]:
        """Generate random dictionary."""
        return {
            StringFactory.random_string(8): NumberFactory.random_int()
            for _ in range(size)
        }

    @staticmethod
    def random_list(size: int = 10, item_type: str = "int") -> List[Any]:
        """Generate random list."""
        generators = {
            "int": NumberFactory.random_int,
            "str": lambda: StringFactory.random_string(),
            "float": NumberFactory.random_float,
        }
        generator = generators.get(item_type, NumberFactory.random_int)
        return [generator() for _ in range(size)]


class ModelFactory:
    """Generic model factory."""

    @staticmethod
    def build(
        model_class: Type[T],
        overrides: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> T:
        """Build model instance with random data.

        Example:
            user = ModelFactory.build(User, email="test@example.com")
        """
        data = kwargs.copy()
        if overrides:
            data.update(overrides)

        # Fill in missing fields with random data
        if hasattr(model_class, "__annotations__"):
            for field_name, field_type in model_class.__annotations__.items():
                if field_name not in data:
                    data[field_name] = ModelFactory._generate_value(field_type)

        return model_class(**data)

    @staticmethod
    def batch(
        model_class: Type[T], count: int = 10, **kwargs
    ) -> List[T]:
        """Build multiple model instances."""
        return [ModelFactory.build(model_class, **kwargs) for _ in range(count)]

    @staticmethod
    def _generate_value(field_type: Type) -> Any:
        """Generate random value for field type."""
        type_str = str(field_type)

        if "int" in type_str:
            return NumberFactory.random_int()
        elif "float" in type_str:
            return NumberFactory.random_float()
        elif "str" in type_str:
            return StringFactory.random_string()
        elif "bool" in type_str:
            return NumberFactory.random_bool()
        elif "datetime" in type_str:
            return DateFactory.random_datetime()
        elif "list" in type_str:
            return []
        elif "dict" in type_str:
            return {}
        else:
            return None


@dataclass
class UserFactory:
    """Factory for creating test users."""

    id: int = field(default_factory=Factory.sequence)
    username: str = field(default_factory=lambda: StringFactory.random_string(8))
    email: str = field(default_factory=StringFactory.random_email)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, **overrides) -> "UserFactory":
        """Create user with overrides."""
        return cls(**overrides)

    @classmethod
    def batch(cls, count: int = 10) -> List["UserFactory"]:
        """Create multiple users."""
        return [cls.create() for _ in range(count)]


@dataclass
class OrderFactory:
    """Factory for creating test orders."""

    id: int = field(default_factory=Factory.sequence)
    user_id: int = field(default_factory=lambda: NumberFactory.random_int(1, 1000))
    total: float = field(default_factory=lambda: NumberFactory.random_float(10, 1000))
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create(cls, **overrides) -> "OrderFactory":
        """Create order with overrides."""
        return cls(**overrides)

    @classmethod
    def batch(cls, count: int = 10) -> List["OrderFactory"]:
        """Create multiple orders."""
        return [cls.create() for _ in range(count)]


class PerformanceDataFactory:
    """Factory for generating performance test data."""

    @staticmethod
    def large_string(size_mb: float = 1.0) -> str:
        """Generate large string for testing."""
        size_bytes = int(size_mb * 1024 * 1024)
        return "x" * size_bytes

    @staticmethod
    def large_list(size: int = 10000) -> List[Dict[str, Any]]:
        """Generate large list for testing."""
        return [
            {
                "id": i,
                "name": StringFactory.random_string(),
                "value": NumberFactory.random_float(),
            }
            for i in range(size)
        ]

    @staticmethod
    def nested_dict(depth: int = 5, width: int = 3) -> Dict[str, Any]:
        """Generate nested dictionary for testing."""
        if depth == 0:
            return {"value": NumberFactory.random_int()}

        return {
            f"key_{i}": PerformanceDataFactory.nested_dict(depth - 1, width)
            for i in range(width)
        }
