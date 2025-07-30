"""
Tests for the hello module.
"""

from flex_evals.hello import hello_world, get_version


def test_hello_world_default():
    """Test hello_world with default parameter."""
    result = hello_world()
    assert result == "Hello, World!"


def test_hello_world_with_name():
    """Test hello_world with custom name."""
    result = hello_world("Python")
    assert result == "Hello, Python!"


def test_hello_world_empty_string():
    """Test hello_world with empty string."""
    result = hello_world("")
    assert result == "Hello, !"


def test_get_version():
    """Test get_version function."""
    version = get_version()
    assert isinstance(version, str)
    assert version == "0.0.1"


def test_hello_world_type():
    """Test that hello_world returns a string."""
    result = hello_world("Test")
    assert isinstance(result, str)