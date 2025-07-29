"""Tests for the PostgreSQL client with actual database connection."""
from pathlib import Path

import pytest
import pytest_asyncio  # type: ignore[import]
from dotenv import load_dotenv  # type: ignore[import]

from prs_commons.db import PostgresClient

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Configure pytest
pytest_plugins = ('pytest_asyncio',)
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
async def db_client():
    """Create and return a database client for testing."""
    client = PostgresClient()
    await client.connect()
    
    try:
        # Create test schema if it doesn't exist
        await client.execute(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}")
        
        # Create test table
        await client.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TEST_SCHEMA}.{TEST_TABLE} (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        # Clear any existing test data
        await client.execute(f"TRUNCATE TABLE {TEST_SCHEMA}.{TEST_TABLE} CASCADE")
        
        yield client
        
    finally:
        # Clean up
        try:
            # Drop test schema and all objects in it
            await client.execute(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE")
        except Exception as e:
            print(f"Error during teardown: {e}")
        finally:
            await client.disconnect()


class TestPostgresClient:
    """Test cases for the PostgreSQL client with actual database connection."""

    @pytest.mark.asyncio
    async def test_connect_disconnect(self, db_client):
        """Test connecting and disconnecting from the database."""
        assert db_client._pool is not None
        
        # Test reconnection
        await db_client.disconnect()
        assert db_client._pool is None
        
        await db_client.connect()
        assert db_client._pool is not None
    
    @pytest.mark.asyncio
    async def test_fetch_one(self, db_client, test_schema, test_table):
        """Test fetching a single row from the database."""
        # Insert test data
        await db_client.execute(
            f"""
            INSERT INTO {test_schema}.{test_table} (name, value, is_active)
            VALUES ('test', 42, TRUE)
            """
        )
        
        # Fetch the inserted row (returns a tuple)
        result = await db_client.fetch_one(
            f"SELECT * FROM {test_schema}.{test_table} WHERE name = 'test'"
        )
        
        # Result is a tuple (id, name, value, is_active, created_at)
        assert result is not None
        assert len(result) >= 4  # At least 4 columns
        assert result['name'] == 'test'  # name
        assert result['value'] == 42      # value
        assert result['is_active'] is True    # is_active
    
    @pytest.mark.asyncio
    async def test_fetch_all(self, db_client, test_schema, test_table):
        """Test fetching multiple rows from the database."""
        # Insert test data
        for i in range(3):
            await db_client.execute(
                f"""
                INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                VALUES ('test_{i}', {i}, {i % 2 == 0})
                """.format(i=i)
            )
        
        # Fetch all active rows (returns list of dicts)
        results = await db_client.fetch_all(
            f"SELECT * FROM {test_schema}.{test_table} WHERE is_active = TRUE ORDER BY value"
        )
        
        # Should get 2 rows (indices 0 and 2)
        assert len(results) == 2
        for i, row in enumerate(results):
            assert row['name'] == f'test_{i*2}'  # name
            assert row['value'] == i * 2          # value
            assert row['is_active'] is True       # is_active
    
    @pytest.mark.asyncio
    async def test_execute_returning(self, db_client, test_schema, test_table):
        """Test executing a write operation that returns data."""
        # Insert a row and return the ID
        success, result = await db_client.execute_returning(
            f"""
            INSERT INTO {test_schema}.{test_table} (name, value, is_active)
            VALUES ('returning_test', 200, TRUE)
            RETURNING id, name
            """
        )
        
        # execute_returning returns a tuple of (success, result)
        assert success is True
        assert 'id' in result
        assert result['name'] == 'returning_test'
    
    @pytest.mark.asyncio
    async def test_transaction(self, db_client, test_schema, test_table):
        """Test transaction support with rollback."""
        try:
            async with db_client.connection() as conn:
                # Start a transaction
                await conn.execute(
                    f"""
                    INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                    VALUES ('transaction_test', 300, TRUE)
                    """
                )
                # The transaction will be rolled back automatically on error
                
                # Verify the row exists within the transaction
                result = await conn.fetch_one(
                    f"SELECT * FROM {test_schema}.{test_table} "
                    "WHERE name = 'transaction_test'"
                )
                assert result is not None
                
                # This will cause the transaction to roll back
                raise Exception("Intentional rollback")
        except Exception:
            pass
        
        # Outside the transaction, the row should not exist
        result = await db_client.fetch_one(
            f"SELECT * FROM {test_schema}.{test_table} "
            "WHERE name = 'transaction_test'"
        )
        assert result is None
    
    @pytest.mark.asyncio
    async def test_nested_transactions(self, db_client, test_schema, test_table):
        """Test nested transactions with savepoints."""
        try:
            async with db_client.connection() as conn:
                # Outer transaction - insert a user
                await conn.execute(
                    f"""
                    INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                    VALUES ('nested_outer', 400, TRUE)
                    """
                )
                
                try:
                    # Inner transaction (savepoint) - insert an account
                    async with conn.transaction():
                        await conn.execute(
                            f"""
                            INSERT INTO {test_schema}.{test_table} (name, value, is_active)
                            VALUES ('nested_inner', 500, TRUE)
                            """
                        )
                        # This will roll back only the inner transaction
                        raise Exception("Intentional inner rollback")
                        
                except Exception as e:
                    assert str(e) == "Intentional inner rollback"
                    # Verify inner transaction was rolled back
                    inner_result = await db_client.fetch_one(
                        f"SELECT * FROM {test_schema}.{test_table} "
                        "WHERE name = 'nested_inner'"
                    )
                    assert inner_result is None
                    
                    # Continue with outer transaction
                    await conn.execute(
                        f"""
                        UPDATE {test_schema}.{test_table}
                        SET value = 450
                        WHERE name = 'nested_outer'
                        """
                    )
                
                # This will roll back the entire transaction
                raise Exception("Intentional outer rollback")
                
        except Exception as e:
            assert str(e) == "Intentional outer rollback"
        
        # Verify both inner and outer transactions were rolled back
        outer_result = await db_client.fetch_one(
            f"SELECT * FROM {test_schema}.{test_table} "
            "WHERE name = 'nested_outer'"
        )
        assert outer_result is None
