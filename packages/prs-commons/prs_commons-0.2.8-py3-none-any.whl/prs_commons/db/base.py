"""Base database interfaces and abstract classes."""

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

# Type variable for generic database connection types
T = TypeVar("T")  # Generic type for database connection


class DatabaseConnection:
    """Base class for database connections."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def get_connection(self) -> AbstractAsyncContextManager[T]:
        """Get a managed database connection with transaction support.

        Returns:
            AbstractAsyncContextManager[T]: An async context manager that
            yields a database connection.
        """
        pass


class DatabaseClient(ABC):
    """Abstract base class for database clients."""

    @abstractmethod
    async def fetch_one(
        self, connection: Any, query: str, *args: Any
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        pass

    @abstractmethod
    async def fetch_all(
        self, connection: Any, query: str, *args: Any
    ) -> List[Dict[str, Any]]:
        """Fetch multiple rows from the database."""
        pass

    @abstractmethod
    async def execute(
        self, connection: Any, query: str, *args: Any
    ) -> Tuple[bool, Union[int, str]]:
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        pass

    @abstractmethod
    async def execute_returning(
        self, connection: Any, query: str, *args: Any
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Execute a query that returns the affected row."""
        pass
