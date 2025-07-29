"""
Base storage client interface.

This module defines the abstract base class for all storage clients
and common exceptions used across storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar

# Type for the underlying client implementation
BaseClientType = Any

T = TypeVar("T", bound="StorageClient")


class StorageClient(ABC):
    """Abstract base class for storage clients.

    This class defines the common interface that all storage clients must implement.
    """

    @property
    @abstractmethod
    def client(self) -> BaseClientType:
        """Get the underlying storage client instance.

        Returns:
            The client instance used to interact with the storage service.

        Raises:
            RuntimeError: If the client cannot be initialized.
        """
        pass

    @abstractmethod
    async def upload_file(
        self, file_path: str, bucket: str, key: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Upload a file to storage.

        Args:
            file_path: Path to the local file
            bucket: Target bucket name
            key: Object key (path in the bucket)
            **kwargs: Additional implementation-specific arguments

        Returns:
            Dictionary containing status and operation details
        """
        pass

    @abstractmethod
    async def download_file(
        self, bucket: str, key: str, file_path: str, **kwargs: Any
    ) -> bool:
        """Download a file from storage.

        Args:
            bucket: Source bucket name
            key: Object key (path in the bucket)
            file_path: Local filesystem path where the file will be saved
            **kwargs: Additional implementation-specific arguments

        Returns:
            bool: True if the file was downloaded successfully, False otherwise
        """
        pass

    @abstractmethod
    async def delete_object(self, bucket: str, key: str) -> Dict[str, Any]:
        """Delete an object from storage.

        Args:
            bucket: Bucket name
            key: Object key to delete

        Returns:
            Dictionary containing status and operation details
        """
        pass

    @abstractmethod
    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        operation: str = "get_object",
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for an object.

        Args:
            bucket: Bucket name
            key: Object key
            operation: The operation to allow with this URL
            expiration: Time in seconds until the URL expires
            **kwargs: Additional parameters for the operation

        Returns:
            Pre-signed URL as string, or None if credentials are invalid
        """
        pass

    @abstractmethod
    async def generate_upload_url(
        self, bucket: str, key: str, expiration: int = 3600, **kwargs: Any
    ) -> Optional[str]:
        """Generate a pre-signed URL for uploading a file.

        Args:
            bucket: Bucket name
            key: Object key where the file will be stored
            expiration: Time in seconds until the URL expires
            **kwargs: Additional parameters for the put_object operation

        Returns:
            Pre-signed URL as string, or None if credentials are invalid
        """
        pass

    @abstractmethod
    async def generate_download_url(
        self, bucket: str, key: str, expiration: int = 3600, **kwargs: Any
    ) -> Optional[str]:
        """Generate a pre-signed URL for downloading a file.

        Args:
            bucket: Bucket name
            key: Object key of the file to download
            expiration: Time in seconds until the URL expires
            **kwargs: Additional parameters for the get_object operation

        Returns:
            Pre-signed URL as string, or None if credentials are invalid
        """
        pass

    @abstractmethod
    async def upload_string_as_file(
        self, bucket: str, key: str, data: str, **kwargs: Any
    ) -> Optional[str]:
        """Upload a file from a base64-encoded string.

        Args:
            bucket: Bucket name
            key: Object key where the file will be stored
            data: Base64-encoded string of the file contents
            **kwargs: Additional arguments for the upload operation

        Returns:
            Optional[str]: The uploaded file's key, or None if upload fails
        """
        pass

    @abstractmethod
    async def download_as_base64(
        self, bucket: str, key: str, check_exists: bool = True, **kwargs: Any
    ) -> Optional[str]:
        """Download a file and return its contents as a base64-encoded string.

        Args:
            bucket: Bucket name
            key: Object key to download
            check_exists: If True, check if the object exists before downloading
            **kwargs: Additional arguments for the download operation

        Returns:
            Base64-encoded string of the file contents, or None if download fails
        """
        pass

    @abstractmethod
    async def file_exists(self, bucket: str, key: str) -> bool:
        """Check if a file exists in the bucket.

        Args:
            bucket: Bucket name
            key: Object key to check

        Returns:
            True if the file exists, False otherwise
        """
        pass
