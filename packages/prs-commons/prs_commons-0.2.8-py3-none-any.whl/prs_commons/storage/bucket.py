"""
Bucket interface and implementations for different storage backends.

This module defines a generic Bucket interface and provides implementations
for different storage backends like S3, GCS, etc.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Union


class BucketClient(ABC):
    """Abstract base class for bucket storage clients."""

    @abstractmethod
    def upload_file(
        self,
        file_path: Union[str, Path],
        key: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Upload a file to the bucket.

        Args:
            file_path: Path to the local file to upload
            key: Key/path to store the file in the bucket
            metadata: Optional metadata to attach to the file

        Returns:
            Dict containing operation status and metadata
        """
        pass

    @abstractmethod
    def download_file(self, key: str, local_path: Union[str, Path]) -> Dict[str, str]:
        """Download a file from the bucket.

        Args:
            key: Key/path of the file in the bucket
            local_path: Local path to save the downloaded file

        Returns:
            Dict containing operation status and metadata
        """
        pass

    @abstractmethod
    def delete_file(self, key: str) -> Dict[str, str]:
        """Delete a file from the bucket.

        Args:
            key: Key/path of the file to delete

        Returns:
            Dict containing operation status
        """
        pass

    @abstractmethod
    def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a pre-signed URL for a file.

        Args:
            key: Key/path of the file
            expires_in: URL expiration time in seconds

        Returns:
            Pre-signed URL string
        """
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[Dict[str, str]]:
        """List files in the bucket.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            List of file metadata dictionaries
        """
        pass

    @abstractmethod
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in the bucket.

        Args:
            key: Key/path of the file

        Returns:
            True if file exists, False otherwise
        """
        pass
