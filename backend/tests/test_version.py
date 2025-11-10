"""Test version information."""
import unistax


def test_version_exists():
    """Test that version attribute exists."""
    assert hasattr(unistax, "__version__")
    assert isinstance(unistax.__version__, str)
