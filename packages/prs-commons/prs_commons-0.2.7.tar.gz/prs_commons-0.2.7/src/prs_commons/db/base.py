"""Base database interfaces and abstract classes."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class DatabaseClient(ABC):
    """Abstract base class for database clients."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    async def fetch_one(
        self, query: str, *args: Any
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        pass

    @abstractmethod
    async def fetch_all(
        self, query: str, *args: Any
    ) -> List[Dict[str, Any]]:
        """Fetch multiple rows from the database."""
        pass

    @abstractmethod
    async def execute(
        self, query: str, *args: Any
    ) -> Tuple[bool, Union[int, str]]:
        """Execute a write query (INSERT, UPDATE, DELETE)."""
        pass

    @abstractmethod
    async def execute_returning(
        self, query: str, *args: Any
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Execute a query that returns the affected row."""
        pass
