"""Property-based testing utilities using Hypothesis."""

from typing import Any, Callable, Dict, List, Optional
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.strategies import SearchStrategy


class PropertyStrategies:
    """Strategies for property-based testing."""

    # Basic types
    small_int = st.integers(min_value=0, max_value=1000)
    large_int = st.integers(min_value=1000, max_value=1000000)
    positive_int = st.integers(min_value=1, max_value=1000000)
    port_number = st.integers(min_value=1024, max_value=65535)

    small_float = st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    percentage = st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)

    # Strings
    ascii_text = st.text(alphabet=st.characters(blacklist_categories=("Cs",)), min_size=1, max_size=100)
    alphanumeric = st.text(alphabet=st.characters(whitelist_categories=("L", "N")), min_size=1, max_size=50)
    email = st.emails()
    url = st.from_regex(r"https?://[a-z0-9.-]+\.[a-z]{2,}", fullmatch=True)

    # Collections
    small_list = st.lists(st.integers(), min_size=0, max_size=10)
    medium_list = st.lists(st.integers(), min_size=10, max_size=100)
    large_list = st.lists(st.integers(), min_size=100, max_size=1000)

    small_dict = st.dictionaries(
        keys=st.text(min_size=1, max_size=10),
        values=st.integers(),
        min_size=0,
        max_size=10
    )

    # Timestamps
    timestamp = st.datetimes()
    recent_timestamp = st.datetimes(
        min_value=None,  # Use defaults
        max_value=None
    )

    # Status codes
    http_status = st.sampled_from([200, 201, 204, 400, 401, 403, 404, 500, 502, 503])
    error_code = st.sampled_from(["ERR001", "ERR002", "ERR003", "ERR404", "ERR500"])

    # Config values
    cache_ttl = st.integers(min_value=60, max_value=3600)
    pool_size = st.integers(min_value=1, max_value=50)
    timeout = st.floats(min_value=0.1, max_value=30.0, allow_nan=False)

    @staticmethod
    def json_dict() -> SearchStrategy:
        """Generate JSON-serializable dictionaries."""
        return st.recursive(
            st.none() | st.booleans() | st.integers() | st.floats(allow_nan=False) | st.text(),
            lambda children: st.lists(children) | st.dictionaries(st.text(), children),
            max_leaves=10
        )


class PropertyTest:
    """Helper for property-based testing."""

    @staticmethod
    def test_idempotent(func: Callable, strategy: SearchStrategy):
        """Test that function is idempotent.

        Example:
            @PropertyTest.test_idempotent(my_func, st.integers())
            def test_my_func_idempotent(value):
                result1 = my_func(value)
                result2 = my_func(value)
                assert result1 == result2
        """
        @given(strategy)
        def test(value):
            result1 = func(value)
            result2 = func(value)
            assert result1 == result2, f"Function not idempotent for {value}"

        return test

    @staticmethod
    def test_commutative(func: Callable, strategy: SearchStrategy):
        """Test that function is commutative.

        Example:
            @PropertyTest.test_commutative(add, st.integers())
            def test_add_commutative(a, b):
                assert add(a, b) == add(b, a)
        """
        @given(strategy, strategy)
        def test(a, b):
            assert func(a, b) == func(b, a), f"Function not commutative for {a}, {b}"

        return test

    @staticmethod
    def test_associative(func: Callable, strategy: SearchStrategy):
        """Test that function is associative."""
        @given(strategy, strategy, strategy)
        def test(a, b, c):
            result1 = func(func(a, b), c)
            result2 = func(a, func(b, c))
            assert result1 == result2, f"Function not associative for {a}, {b}, {c}"

        return test


class InvariantChecker:
    """Check invariants in data structures."""

    @staticmethod
    def check_sorted(items: List[Any]) -> bool:
        """Check if list is sorted."""
        return all(items[i] <= items[i + 1] for i in range(len(items) - 1))

    @staticmethod
    def check_unique(items: List[Any]) -> bool:
        """Check if all items are unique."""
        return len(items) == len(set(items))

    @staticmethod
    def check_range(value: float, min_val: float, max_val: float) -> bool:
        """Check if value is in range."""
        return min_val <= value <= max_val

    @staticmethod
    def check_non_empty(items: List[Any]) -> bool:
        """Check if collection is non-empty."""
        return len(items) > 0

    @staticmethod
    def check_size_limit(items: List[Any], max_size: int) -> bool:
        """Check if collection size is within limit."""
        return len(items) <= max_size


# Common test settings
fast_settings = settings(
    max_examples=10,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None
)

thorough_settings = settings(
    max_examples=1000,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None
)


def property_test(strategy: SearchStrategy, **kwargs):
    """Decorator for property-based tests.

    Example:
        @property_test(st.integers(min_value=0, max_value=100))
        def test_sqrt(n):
            result = sqrt(n)
            assert result * result <= n < (result + 1) * (result + 1)
    """
    return given(strategy, **kwargs)
