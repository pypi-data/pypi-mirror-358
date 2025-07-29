from __future__ import annotations

import logging
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from asyncpg import Connection, PostgresError
from typing_extensions import override

from prs_commons.db.base import DatabaseClient

_logger = logging.getLogger(__name__)


class PostgresClient(DatabaseClient):
    """High-level asynchronous PostgreSQL database client.

    This class provides a convenient interface for executing database operations
    while delegating connection pooling and transaction management to the
    underlying `PostgresConnection` instance. It implements the singleton pattern
    to ensure consistent database access throughout the application.

    Key Features:
    - High-level query execution methods (fetch_one, fetch_all, execute)
    - Transaction management through the connection context manager
    - Type hints and comprehensive error handling

    Note:
        Connection pooling is managed by the `PostgresConnection` class.
        This class serves as a thin wrapper that provides a more convenient API
        for common database operations.

    Args:
        dsn: The connection string for the PostgreSQL database.
             If not provided, it will be constructed from environment
             variables (DB_USER, DB_PASSWORD, etc.)
        min_size: Minimum number of connections to keep in the pool (default: 1)
        max_size: Maximum number of connections in the pool (default: 50)
    """

    _instance: ClassVar[Optional[PostgresClient]] = None
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> PostgresClient:
        """Ensure only one instance of PostgresClient exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the PostgreSQL client.

        Note: This will only initialize the instance once due to the singleton pattern.
        Subsequent calls with different parameters will be ignored.
        """
        if self._initialized:
            return
        self._initialized = True

    @override
    async def fetch_one(
        self,
        connection: Connection,
        query: str,
        *args: Any,
        timeout: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database.

        Args:
            query: The SQL query to execute
            *args: Query parameters
            timeout: Optional timeout in seconds

        Returns:
            A dictionary representing the row, or None if no rows were found
        """
        row = await connection.fetchrow(query, *args, timeout=timeout)
        return dict(row) if row else None

    @override
    async def fetch_all(
        self,
        connection: Connection,
        query: str,
        *args: Any,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch multiple rows from the database.

        Args:
            query: The SQL query to execute
            *args: Query parameters
            timeout: Optional timeout in seconds

        Returns:
            A list of dictionaries, where each dictionary represents a row
        """
        rows = await connection.fetch(query, *args, timeout=timeout)
        return [dict(row) for row in rows]

    @override
    async def execute(
        self,
        connection: Connection,
        query: str,
        *args: Any,
        timeout: Optional[float] = None,
    ) -> Tuple[bool, Union[int, str]]:
        """Execute a write query (INSERT, UPDATE, DELETE) and return the result.

        This is a convenience method for executing write operations without explicit
        transaction management. Each call runs in its own transaction.

        Args:
            query: The SQL query to execute
            *args: Query parameters
            timeout: Optional timeout in seconds

        Returns:
            Tuple[bool, Union[int, str]]:
                - (True, affected_rows) on success
                - (False, error_message) on failure

        Example:
            ```python
            success, result = await db.execute(
                "UPDATE users SET active = $1 WHERE id = $2",
                True, 123
            )
            if success:
                print(f"Updated {result} rows")
            ```
        """
        try:
            async with connection.transaction():
                result = await connection.execute(query, *args, timeout=timeout)
                if result.startswith(("INSERT", "UPDATE", "DELETE")):
                    # Extract the number of affected rows
                    return True, int(result.split()[-1])
                return True, result
        except (PostgresError, ValueError) as e:
            _logger.error("Error executing query: %s", str(e), exc_info=True)
            return False, str(e)

    @override
    async def execute_returning(
        self,
        connection: Connection,
        query: str,
        *args: Any,
        timeout: Optional[float] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Execute a query that returns the affected row.

        Args:
            query: The SQL query to execute
            *args: Query parameters
            timeout: Optional timeout in seconds

        Returns:
            A tuple of (success, result_dict) where result_dict is the affected row
            or None if no rows were affected
        """
        try:
            async with connection.transaction():
                row = await connection.fetchrow(query, *args, timeout=timeout)
                return True, dict(row) if row else None
        except PostgresError as e:
            _logger.error(
                "Error executing query with return: %s", str(e), exc_info=True
            )
            return False, None
