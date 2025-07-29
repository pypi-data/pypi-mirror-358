"""Tests for Odoo RPC client functionality with real connection."""

import os

import pytest
import pytest_asyncio

from prs_commons import OdooRPClient

# Skip tests if required environment variables are not set
pytestmark = pytest.mark.skipif(
    not all(
        os.getenv(var)
        for var in ["ODOO_HOST", "ODOO_DB", "ODOO_LOGIN", "ODOO_PASSWORD"]
    ),
    reason="Odoo connection environment variables not set",
)

pytest_plugins = ("pytest_asyncio",)

# Add async support for fixtures
pytestmark = pytest.mark.asyncio(scope="module")


class TestOdooRPClientRealConnection:
    """Test suite for OdooRPClient with real connection."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        """Setup test environment before each test method."""
        # Clear the singleton instance before each test
        OdooRPClient._instance = None
        OdooRPClient._initialized = False
        self.client = OdooRPClient()
        yield
        # Cleanup after test if needed

    async def test_ensure_connection_WithValidCredentials_ShouldConnectSuccessfully(
        self,
    ):
        """Test that ensure_connection succeeds with valid Odoo credentials."""
        # This will raise an exception if connection fails
        self.client.ensure_connection()

        # Verify client is connected
        print(self.client)
        assert self.client.client is not None

        # Try a simple RPC call to verify connection works
        try:
            # Get server version as a simple test
            version = self.client.client.version
            assert version is not None
            print(f"Connected to Odoo version: {version}")
        except Exception as e:
            pytest.fail(f"Failed to get Odoo version: {str(e)}")

    async def test_OdooRPClient_WhenInstantiatedMultipleTimes_ShouldReturnSameInstance(
        self,
    ):
        """Test that OdooRPClient follows singleton
        pattern and returns same instance."""
        # Create first instance and connect
        client1 = OdooRPClient()
        client1.ensure_connection()

        # Create second instance
        client2 = OdooRPClient()

        # Both should be the same instance
        assert client1 is client2

        # Both should be connected
        assert client1.client is not None
        assert client2.client is not None
        assert client1.client is client2.client

    async def test_search_read_WithValidUserCredentials_ShouldReturnUserData(self):
        """Test that search_read returns correct user data for authenticated user."""
        # Ensure connection is established
        self.client.ensure_connection()

        # Get the current user's login from environment variables
        expected_login = os.getenv("ODOO_LOGIN")
        assert expected_login is not None, "ODOO_LOGIN environment variable not set"

        # Search for the current user by login
        users = self.client.search_read(
            model="res.users",
            domain=[("login", "=", expected_login)],
            fields=["id", "name", "login"],
        )

        # Verify we found exactly one user
        assert (
            len(users) == 1
        ), f"Expected exactly one user with login {expected_login}, found {len(users)}"
        user_data = users[0]

        # Verify the data
        assert (
            user_data["login"] == expected_login
        ), f"Expected login '{expected_login}' but got '{user_data['login']}'"
        assert user_data.get("name"), "User name should not be empty"

        print(f"Logged in as: {user_data['name']} ({user_data['login']})")

        # Verify we can also get the user by ID
        user_by_id = self.client.search_read(
            model="res.users",
            domain=[("id", "=", user_data["id"])],
            fields=["name", "login"],
        )
        assert len(user_by_id) == 1
        assert user_by_id[0]["login"] == expected_login
