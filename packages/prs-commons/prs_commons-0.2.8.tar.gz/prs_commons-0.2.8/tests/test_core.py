"""Tests for the core functionality of prs-commons."""

import sys
from pathlib import Path

# Add the parent directory to Python path before imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the project modules
import pytest  # noqa: E402

from prs_commons import __version__  # noqa: E402
from prs_commons.core import MyClass  # noqa: E402


def test_myclass_init():
    """Test MyClass initialization."""
    obj = MyClass("Test")
    assert obj.name == "Test"


def test_myclass_greet():
    """Test the greet method of MyClass."""
    obj = MyClass("World")
    assert obj.greet() == "Hello, World!"


def test_myclass_version():
    """Test the version method of MyClass."""
    assert MyClass.version() == __version__


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Alice", "Hello, Alice!"),
        ("Bob", "Hello, Bob!"),
        ("", "Hello, !"),
    ],
)
def test_myclass_greet_parametrized(name, expected):
    """Test greet method with different parameters."""
    obj = MyClass(name)
    assert obj.greet() == expected
