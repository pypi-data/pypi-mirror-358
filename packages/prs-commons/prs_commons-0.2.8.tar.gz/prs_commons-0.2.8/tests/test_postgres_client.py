"""Tests for the PostgreSQL client with actual database connection."""

from pathlib import Path

import pytest
import pytest_asyncio
from asyncpg import Connection
from dotenv import load_dotenv

from prs_commons.db import PostgresClient, PostgresConnection

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Configure pytest
pytest_plugins = ("pytest_asyncio",)
pytestmark = pytest.mark.asyncio

# Test configuration
TEST_TABLE = "test_table"
TEST_SCHEMA = "test_schema"


@pytest.fixture
def test_schema():
    """Return the test schema name."""
    return TEST_SCHEMA


@pytest.fixture
def test_table():
    """Return the test table name."""
    return TEST_TABLE


@pytest_asyncio.fixture
async def db_connection():
    """Create and return a database connection for testing."""
    pg_connection = PostgresConnection()
    await pg_connection.connect()
    try:
        async with pg_connection.get_connection() as conn:
            yield conn
    finally:
        await pg_connection.disconnect()


@pytest_asyncio.fixture
async def db_client():
    """Create and return a database client for testing."""
    return PostgresClient()


@pytest_asyncio.fixture
async def test_db(db_connection: Connection, db_client: PostgresClient):
    """Set up test database schema and tables."""
    # Create test schema if it doesn't exist

    await db_connection.execute(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}")

    # Create test table
    await db_connection.execute(
        f"""
            CREATE TABLE IF NOT EXISTS {TEST_SCHEMA}.{TEST_TABLE} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
    )

    # Clear any existing test data
    await db_connection.execute(f"TRUNCATE TABLE {TEST_SCHEMA}.{TEST_TABLE} CASCADE")

    yield db_client, db_connection

    # Clean up
    await db_connection.execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")


class TestPostgresClient:
    """Test cases for the PostgreSQL client with actual database connection."""

    @pytest.mark.asyncio
    async def test_fetch_one(self, test_db, test_schema, test_table):
        """Test fetching a single row from the database."""
        db_client, db_connection = test_db

        # Insert test data
        await db_client.execute(
            db_connection,
            f"""
            INSERT INTO {test_schema}.{test_table} (name, value, is_active)
            VALUES ('test', 42, TRUE)
            """,
        )

        # Fetch the inserted row
        result = await db_client.fetch_one(
            db_connection,
            f"SELECT * FROM {test_schema}.{test_table} WHERE name = 'test'",
        )

        assert result is not None
        assert "id" in result
        assert result["name"] == "test"
        assert result["value"] == 42
        assert result["is_active"] is True

    @pytest.mark.asyncio
    async def test_fetch_all(self, test_db, test_schema, test_table):
        """Test fetching multiple rows from the database."""
        db_client, db_connection = test_db

        # Insert test data
        for i in range(3):
            await db_client.execute(
                db_connection,
                f"""
                INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                VALUES ('test_{i}', {i}, {i % 2 == 0})
                """,
            )

        # Fetch all active rows
        results = await db_client.fetch_all(
            db_connection,
            f"""SELECT * FROM {test_schema}.{test_table}
            WHERE is_active = TRUE ORDER BY value""",
        )

        # Should get 2 rows (indices 0 and 2)
        assert len(results) == 2
        for i, row in enumerate(results):
            assert row["name"] == f"test_{i*2}"
            assert row["value"] == i * 2
            assert row["is_active"] is True

    @pytest.mark.asyncio
    async def test_execute_returning(self, test_db, test_schema, test_table):
        """Test executing a write operation that returns data."""
        db_client, db_connection = test_db

        # Insert a row and return the ID
        success, result = await db_client.execute_returning(
            db_connection,
            f"""
            INSERT INTO {test_schema}.{test_table} (name, value, is_active)
            VALUES ('returning_test', 200, TRUE)
            RETURNING id, name
            """,
        )

        # execute_returning returns a tuple of (success, result)
        assert success is True
        assert "id" in result
        assert result["name"] == "returning_test"

    @pytest.mark.asyncio
    async def test_transaction(self, test_db, test_schema, test_table):
        """Test transaction support with rollback."""
        db_client, conn = test_db

        # Test transaction rollback
        try:
            async with conn.transaction():
                await conn.execute(
                    f"""
                    INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                    VALUES ('transaction_test', 300, TRUE)
                    """
                )

                # Verify the row exists within the transaction
                result = await conn.fetchrow(
                    f"SELECT * FROM {test_schema}.{test_table} "
                    "WHERE name = 'transaction_test'"
                )
                assert result is not None

                # This will cause the transaction to roll back
                raise Exception("Intentional rollback")
        except Exception as e:
            assert str(e) == "Intentional rollback"

            # Verify the row was rolled back
            result = await conn.fetchrow(
                f"SELECT * FROM {test_schema}.{test_table} "
                "WHERE name = 'transaction_test'"
            )
            assert result is None, "Row should not exist after transaction rollback"

    @pytest.mark.asyncio
    async def test_nested_transactions(self, test_db, test_schema, test_table):
        """Test nested transactions with savepoints."""
        db_client, conn = test_db

        try:
            # Start outer transaction
            async with conn.transaction():
                # Insert a row in the outer transaction
                await conn.execute(
                    f"""
                    INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                    VALUES ('nested_outer', 400, TRUE)
                    """
                )

                # Create a savepoint for the inner transaction
                async with conn.transaction():
                    try:
                        # Insert another row in the inner transaction
                        await conn.execute(
                            f"""
                            INSERT INTO {test_schema}.{test_table}
                            (name, value, is_active)
                            VALUES ('nested_inner', 500, TRUE)
                            """
                        )

                        # This should cause the inner transaction to roll back
                        raise Exception("Intentional inner rollback")

                    except Exception as e:
                        assert str(e) == "Intentional inner rollback"
                        # Re-raise to trigger the rollback of the savepoint
                        raise

                # This code won't be reached because the inner
                # transaction will roll back the savepoint
                # and raise an exception that will be caught by the outer try/except

        except Exception:
            # Verify the outer transaction was rolled back
            outer_result = await conn.fetchrow(
                f"SELECT * FROM {test_schema}.{test_table} "
                "WHERE name = 'nested_outer'"
            )
            assert outer_result is None, "Outer transaction should be rolled back"

            # Verify the inner transaction was rolled back
            inner_result = await conn.fetchrow(
                f"SELECT * FROM {test_schema}.{test_table} "
                "WHERE name = 'nested_inner'"
            )
            assert inner_result is None, "Inner transaction should be rolled back"
