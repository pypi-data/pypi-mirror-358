"""
PRS Facade Common - A Python library for common facade functionality.

This package provides common utilities and clients for PRS microservices,
including Odoo RPC client, AWS clients, and other shared functionality.
"""

from .__version__ import __version__
from .aws import S3Client

# Import key classes/functions to make them available at the package level
from .core import MyClass
from .db.postgres import PostgresClient
from .odoo.rpc_client import OdooRPClient
from .storage.base import StorageClient

__all__ = [
    "__version__",
    "MyClass",
    "OdooRPClient",
    "S3Client",
    "StorageClient",
    "PostgresClient",
]
