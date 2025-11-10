"""Test version information."""
import toolkit


def test_version_exists():
    """Test that version attribute exists."""
    assert hasattr(toolkit, "__version__")
    assert isinstance(toolkit.__version__, str)
