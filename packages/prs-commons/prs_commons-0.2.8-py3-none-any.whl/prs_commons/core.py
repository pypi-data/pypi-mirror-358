"""
Core functionality for the PRS Facade Common library.

This module provides the core functionality used across the PRS Facade system.
"""

__all__ = ["MyClass"]


class MyClass:
    """
    A sample class to demonstrate the library's functionality.

    Attributes:
        name (str): The name to greet.
    """

    def __init__(self, name: str = "World") -> None:
        """Initialize with a name."""
        self.name = name

    def greet(self) -> str:
        """
        Return a greeting message.

        Returns:
            str: A greeting message.
        """
        return "Hello, {}!".format(self.name)

    @staticmethod
    def version() -> str:
        """
        Return the version of the library.

        Returns:
            str: The version string.
        """
        from . import __version__

        return __version__
