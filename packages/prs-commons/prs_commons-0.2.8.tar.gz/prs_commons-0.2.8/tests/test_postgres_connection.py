"""Tests for the PostgresConnection class."""

import pytest

from prs_commons.db import PostgresConnection


class TestPostgresConnection:
    """Test cases for PostgresConnection class."""

    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """Test connecting and disconnecting from the database."""
        db_connection = PostgresConnection()

        # Test initial state
        assert db_connection._pool is None

        # Test connection
        await db_connection.connect()
        assert db_connection._pool is not None

        # Test basic query execution
        async with db_connection.get_connection() as conn:
            assert conn is not None
            result = await conn.fetchval("SELECT 1")
            assert result == 1

        # Test disconnection
        await db_connection.disconnect()
        assert db_connection._pool is None

    @pytest.mark.asyncio
    async def test_connection_context_manager(self):
        """Test the connection context manager."""
        db_connection = PostgresConnection()
        await db_connection.connect()

        try:
            async with db_connection.get_connection() as conn:
                # Test transaction rollback on exception
                try:
                    async with conn.transaction():
                        await conn.execute("CREATE TEMP TABLE test_rollback (id int)")
                        raise Exception("Test rollback")
                except Exception as e:
                    assert str(e) == "Test rollback"

                # Verify table doesn't exist after rollback
                result = await conn.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'test_rollback'
                    )
                    """
                )
                assert result is False
        finally:
            await db_connection.disconnect()
