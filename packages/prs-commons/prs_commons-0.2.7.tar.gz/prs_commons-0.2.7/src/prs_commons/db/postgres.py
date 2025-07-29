"""PostgreSQL database client implementation using asyncpg.

This module provides an async PostgreSQL client that implements the DatabaseClient interface.
It supports connection pooling, query execution, and transaction management with singleton pattern.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, ClassVar, Dict, List, Optional, Tuple, TypeVar, Union

import asyncpg
from typing_extensions import override

from prs_commons.db.base import DatabaseClient

__all__ = ["PostgresClient"]

T = TypeVar("T", bound="PostgresClient")

_logger = logging.getLogger(__name__)


class PostgresClient(DatabaseClient):
    """Asynchronous PostgreSQL database client using asyncpg with singleton pattern.
    
    This client provides a high-level interface for interacting with a PostgreSQL database
    asynchronously using connection pooling. Only one instance of this class will be created
    per process, ensuring a single connection pool is used.
    
    Args:
        dsn: The connection string for the PostgreSQL database
        min_size: Minimum number of connections in the pool (default: 1)
        max_size: Maximum number of connections in the pool (default: 50)
        **kwargs: Additional connection parameters passed to asyncpg.create_pool
    """
    _instance: ClassVar[Optional[PostgresClient]] = None
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> PostgresClient:
        """Ensure only one instance of PostgresClient exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        dsn: Optional[str] = None,
        min_size: int = 1,
        max_size: int = 50,
        **kwargs: Any,
    ) -> None:
        """Initialize the PostgreSQL client.

        Note: This will only initialize the instance once due to the singleton pattern.
        Subsequent calls with different parameters will be ignored.
        """
        if self._initialized:
            return

        self._dsn = dsn or self._build_dsn()
        self._min_size = min_size
        self._max_size = max_size
        self._pool: Optional[asyncpg.Pool] = None
        self._connection_kwargs = kwargs
        self._initialized = True
   
    def _build_dsn(self) -> str:
        """Build a PostgreSQL connection string from environment variables.
        
        Constructs a connection string in the format:
        postgresql://user:password@host:port/database?sslmode=mode
        
        Raises:
            ValueError: If required environment variables (DB_USER, DB_PASSWORD) are not set
            
        Returns:
            str: A connection string suitable for asyncpg.create_pool()
        """
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'postgres')
        ssl = os.getenv('DB_SSLMODE', 'disable')
        
        if not user or not password:
            raise ValueError("DB_USER and DB_PASSWORD environment variables must be set")
            
        return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl}"

    async def connect(self) -> None:
        """Initialize the database connection pool.
        
        Creates a connection pool with the configured parameters. This method is
        called automatically when the first database operation is performed.
        
        The connection pool parameters are:
        - min_size: Minimum number of connections to keep open
        - max_size: Maximum number of connections to allow
        - Other parameters passed during client initialization
        
        Note:
            This method is idempotent - calling it multiple times will only create
            the pool once.
        """
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
                **self._connection_kwargs,
            )
            _logger.info("Created PostgreSQL connection pool")

    async def disconnect(self) -> None:
        """Close all connections in the connection pool.
        
        This method should be called when the database client is no longer needed
        to ensure proper cleanup of resources. After calling this method, the client
        can be reused by calling connect() again.
        
        Note:
            It's good practice to call this when your application shuts down.
        """
        if self._pool:
            await self._pool.close()
            self._pool = None
            _logger.info("Closed PostgreSQL connection pool")

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[asyncpg.Connection]:
        """Get a managed database connection with transaction support.
        
        This context manager provides a connection from the pool and automatically:
        1. Starts a new transaction
        2. Commits on successful completion
        3. Rolls back on any exception
        4. Returns the connection to the pool
        
        Example:
            .. code-block:: python
            
                async with db.connection() as conn:
                    await conn.execute("INSERT INTO table VALUES ($1)", 1)
                    # Changes are committed if no exceptions occur
            
        Yields:
            asyncpg.Connection: A database connection from the pool
            
        Note:
            Nested transactions are supported using savepoints. For example:

            .. code-block:: python

                async with db.connection() as conn:
                    # Outer transaction starts automatically
                    await conn.execute("INSERT INTO users (name) VALUES ('user1')")
                    
                    try:
                        # Start a nested transaction (savepoint)
                        async with conn.transaction():
                            await conn.execute("INSERT INTO accounts (user_id, balance) VALUES (1, 100)")
                            # This savepoint can be rolled back independently
                            raise Exception("Something went wrong")
                            
                    except Exception as e:
                        # Only the inner transaction is rolled back
                        print(f"Caught error: {e}")
                        # The outer transaction continues and will be committed
                        await conn.execute("UPDATE users SET status = 'active' WHERE name = 'user1'")
                    
                    # The outer transaction is committed here if no exceptions
            
            Important:
                If an exception occurs in the outer transaction after an inner transaction
                has committed, the entire transaction (including the committed savepoint)
                will be rolled back. This ensures transaction atomicity - either all
                changes complete successfully, or none of them do.
                
                If you need the inner transaction to persist regardless of the outer
                transaction's outcome, use separate database connections/transactions
                instead of nested transactions.
        """
        if not self._pool:
            await self.connect()
            
        conn = await self._pool.acquire()  # type: ignore[union-attr]
        tr = conn.transaction()
        await tr.start()
        try:
            yield conn
            await tr.commit()
        except Exception:
            await tr.rollback()
            raise
        finally:
            await self._pool.release(conn)  # type: ignore[union-attr]
    
    @override
    async def fetch_one(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single row from the database."""
        if not self._pool:
            await self.connect()
            
        conn = await self._pool.acquire()  # type: ignore[union-attr]
        try:
            row = await conn.fetchrow(query, *args, timeout=timeout)
            return dict(row) if row else None
        finally:
            await self._pool.release(conn)  # type: ignore[union-attr]

    @override
    async def fetch_all(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Fetch multiple rows from the database."""
        if not self._pool:
            await self.connect()
            
        conn = await self._pool.acquire()  # type: ignore[union-attr]
        try:
            rows = await conn.fetch(query, *args, timeout=timeout)
            return [dict(row) for row in rows]
        finally:
            await self._pool.release(conn)  # type: ignore[union-attr]

    @override
    async def execute(
        self, query: str, *args: Any, timeout: Optional[float] = None
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
        if not self._pool:
            await self.connect()
            
        conn = await self._pool.acquire()  # type: ignore[union-attr]
        try:
            result = await conn.execute(query, *args, timeout=timeout)
            if result.startswith(('INSERT', 'UPDATE', 'DELETE')):
                # Extract the number of affected rows
                return True, int(result.split()[-1])
            return True, result
        except (asyncpg.PostgresError, ValueError) as e:
            _logger.error("Error executing query: %s", str(e), exc_info=True)
            return False, str(e)
        finally:
            await self._pool.release(conn)  # type: ignore[union-attr]

    @override
    async def execute_returning(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Execute a query that returns the affected row.
        
        Returns:
            A tuple of (success, result_dict) where result_dict is the affected row
            or None if no rows were affected
        """
        if not self._pool:
            await self.connect()
            
        conn = await self._pool.acquire()  # type: ignore[union-attr]
        try:
            row = await conn.fetchrow(query, *args, timeout=timeout)
            return True, dict(row) if row else None
        except asyncpg.PostgresError as e:
            _logger.error("Error executing query with return: %s", str(e), exc_info=True)
            return False, None
        finally:
            await self._pool.release(conn)  # type: ignore[union-attr]

    async def __aenter__(self) -> 'PostgresClient':
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Async context manager exit."""
        await self.disconnect()
