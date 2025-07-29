"""
Odoo RPC Client for interacting with Odoo's external API.

This module provides a singleton client for making RPC calls to an Odoo instance.
It handles connection management, authentication, and provides common operations.
"""

import os
from typing import Any, Dict, List, Optional, TypeVar, cast

# Import odoorpc for runtime
import odoorpc
from dotenv import load_dotenv

# Type variable for generic model types
T = TypeVar("T")


class OdooRPClient:
    """
    A singleton client for making RPC calls to an Odoo instance.

    This client handles connection management, authentication, and provides
    methods for common Odoo operations. It's implemented as a singleton to
    maintain a single connection pool.

    Environment Variables:
        ODOO_HOST: The hostname of the Odoo server
        ODOO_DB: The database name
        ODOO_LOGIN: The login username
        ODOO_PASSWORD: The login password
    """

    _instance: Optional["OdooRPClient"] = None

    def __new__(cls) -> "OdooRPClient":
        """Ensure only one instance of the client exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the Odoo RPC client with environment configuration."""
        if getattr(self, "_initialized", False):
            return

        load_dotenv()

        self.host = os.getenv("ODOO_HOST")
        self.db = os.getenv("ODOO_DB")
        self.login = os.getenv("ODOO_LOGIN")
        self.password = os.getenv("ODOO_PASSWORD")
        self.protocol = os.environ.get("ODOO_PROTOCOL", "jsonrpc+ssl")
        self.timeout = int(os.environ.get("ODOO_TIMEOUT", "60"))
        self.port = int(os.environ.get("ODOO_PORT", "443"))

        # Use Any type to avoid mypy issues with odoorpc.ODOO
        self.client: Any = None
        self._initialized = True

        # Initialize the Odoo client and ensure we're connected
        self.ensure_connection()

    def ensure_connection(self) -> None:
        """Ensure that we have a valid connection to the Odoo server."""
        if self.client is not None:
            return

        if not all([self.host, self.db, self.login, self.password]):
            raise ConnectionError(
                "Missing required Odoo connection parameters. "
                "Please check your environment variables."
            )

        try:
            # Initialize Odoo client
            self.client = odoorpc.ODOO(
                host=str(self.host),
                protocol=self.protocol,
                timeout=self.timeout,
                port=self.port,
            )
            # Login to Odoo
            self.client.login(
                db=str(self.db), login=str(self.login), password=str(self.password)
            )
        except Exception as e:
            self.client = None
            raise ConnectionError(f"Failed to connect to Odoo server: {str(e)}") from e

    def execute_method(
        self, model: str, method: str, ids: List[int], *args: Any, **kwargs: Any
    ) -> Any:
        """
        Execute a method on a specified model for given record IDs.

        Args:
            model: The Odoo model name (e.g., 'event.registration')
            method: The method name to call
            ids: List of record IDs to operate on
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method

        Returns:
            The result of the method call

        Raises:
            Exception: If the method execution fails
        """
        try:
            self.ensure_connection()
            if self.client is None:  # This should never happen due to ensure_connection
                raise ConnectionError("Not connected to Odoo server")

            model_obj = self.client.env[model]
            return getattr(model_obj, method)(ids, *args, **kwargs)
        except Exception as e:
            self.client = None  # Reset connection on error
            raise Exception(
                f"Failed to execute method {method} on {model}: {str(e)}"
            ) from e

    def search_read(
        self,
        model: str,
        domain: List[tuple],
        fields: Optional[List[str]] = None,
        offset: int = 0,
        limit: Optional[int] = None,
        order: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search and read records from a model.

        Args:
            model: The Odoo model name
            domain: Search domain
            fields: List of fields to return
            offset: Number of records to skip
            limit: Maximum number of records to return
            order: Sort order

        Returns:
            List of dictionaries containing the requested fields for each record
        """
        self.ensure_connection()
        if self.client is None:
            raise ConnectionError("Not connected to Odoo server")

        result = self.client.env[model].search_read(
            domain=domain or [],
            fields=fields or [],
            offset=offset,
            limit=limit,
            order=order,
        )
        return cast(List[Dict[str, Any]], result)

    def create_record(self, model: str, values: Dict[str, Any]) -> int:
        """
        Create a new record in the specified model.

        Args:
            model: The Odoo model name
            values: Dictionary of field values

        Returns:
            The ID of the created record
        """
        self.ensure_connection()
        if self.client is None:
            raise ConnectionError("Not connected to Odoo server")

        result = self.client.env[model].create(values)
        return cast(int, result)

    def write_record(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        """
        Update existing records.

        Args:
            model: The Odoo model name
            ids: List of record IDs to update
            values: Dictionary of field values to update

        Returns:
            True if the update was successful
        """
        self.ensure_connection()
        if self.client is None:
            raise ConnectionError("Not connected to Odoo server")

        result = self.client.env[model].browse(ids).write(values)
        return cast(bool, result)
