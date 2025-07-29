from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, ClassVar, Optional, TypeVar

import asyncpg

from prs_commons.db.base import DatabaseConnection

T = TypeVar("T", bound="PostgresConnection")


_logger = logging.getLogger(__name__)
ConnectionT = TypeVar("ConnectionT", bound=Any)


class PostgresConnection(DatabaseConnection):
    """PostgreSQL database connection manager with connection pooling.

    This class implements the DatabaseConnection interface and provides
    connection pooling and transaction management. It uses a singleton pattern
    to ensure a single connection pool is used per process.

    The connection pool is automatically managed and will be created on first use.
    Connections are automatically returned to the pool when their transaction
    context is exited.
    """

    _instance: ClassVar[Optional[PostgresConnection]] = None
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> PostgresConnection:
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
            ValueError: If required environment variables
            (DB_USER, DB_PASSWORD) are not set

        Returns:
            str: A connection string suitable for asyncpg.create_pool()
        """
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "postgres")
        ssl = os.getenv("DB_SSLMODE", "disable")

        if not user or not password:
            raise ValueError(
                "DB_USER and DB_PASSWORD environment variables must be set"
            )

        return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode={ssl}"

    async def connect(self) -> None:
        """Initialize the database connection pool.

        Creates a connection pool with the configured parameters. This method is
        called automatically when the first connection is requested.

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
    async def get_connection(self) -> AsyncIterator[asyncpg.Connection]:
        """Get a managed database connection with transaction support.

        This context manager provides a connection from the pool with automatic
        transaction management. The connection is automatically returned to the
        pool when the context exits.

        The following operations are performed automatically:

        1. **Starts a new transaction** when entering the context
        2. **Commits** the transaction if the block completes successfully
        3. **Rolls back** the transaction if an exception occurs
        4. **Returns** the connection to the pool when done

        Example:
            .. code-block:: python

                async with db.get_connection() as conn:
                    # Execute queries within a transaction
                    result = await conn.fetch("SELECT * FROM users")
                    # Transaction will be committed if no exceptions occur

        Yields:
            asyncpg.Connection: A database connection from the pool.

        Note:
            The connection and its transaction are managed automatically. Do not
            manually commit or rollback the transaction within the context.

        Note:
            Nested transactions are supported using savepoints. For example:

            .. code-block:: python

                async with db.get_connection() as conn:
                    # Outer transaction starts automatically
                    await conn.execute("INSERT INTO users (name) VALUES ('user1')")


                    try:
                        # Start a nested transaction (savepoint)
                        async with conn.transaction():
                            await conn.execute("INSERT INTO accounts (user_id, balance)
                            VALUES (1, 100)")
                            # This savepoint can be rolled back independently
                            raise Exception("Something went wrong")


                    except Exception as e:
                        # Only the inner transaction is rolled back
                        print(f"Caught error: {e}")
                        # The outer transaction continues and will be committed
                        await conn.execute("UPDATE users
                            SET status = 'active' WHERE name = 'user1'")

                    # The outer transaction is committed here if no exceptions

        Important:
            If an exception occurs in the outer transaction after
            an inner transaction has committed, the entire transaction
            (including the committed savepoint) will be rolled back.
            This ensures transaction atomicity - either all changes
            complete successfully, or none of them do.

            If you need the inner transaction to persist regardless of the outer
            transaction's outcome, use separate database connections/transactions
            instead of nested transactions.
        """
        pool = self._pool
        if pool is None:
            await self.connect()
            pool = self._pool
            if pool is None:
                raise RuntimeError("Failed to connect to the database")

        conn = await pool.acquire()
        tr = conn.transaction()
        await tr.start()
        try:
            yield conn
            await tr.commit()
        except Exception as e:
            await tr.rollback()
            _logger.error("Error in transaction: %s", str(e), exc_info=True)
            raise
        finally:
            if self._pool and not self._pool._closed:
                await self._pool.release(conn)

    async def __aenter__(self) -> "PostgresConnection":
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
