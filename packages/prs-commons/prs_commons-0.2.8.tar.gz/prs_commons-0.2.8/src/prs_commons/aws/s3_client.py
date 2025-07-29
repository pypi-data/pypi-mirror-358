"""Asynchronous S3 client for AWS S3 storage operations.

This module provides a thread-safe singleton S3 client that implements the
StorageClient interface.
"""

import asyncio
import base64
import io
import logging
import os
from contextlib import asynccontextmanager
from threading import Lock
from typing import Any, AsyncGenerator, Dict, Optional, Type, TypeVar

import aioboto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing_extensions import override

from prs_commons.storage.base import StorageClient

# Type aliases
S3Response = Dict[str, Any]

# Type variables for generic class methods
T = TypeVar("T", bound="S3Client")

# Set up logger
logger = logging.getLogger(__name__)


class S3Client(StorageClient):
    """Thread-safe singleton client for AWS S3 operations.

    This client provides an async interface to interact with AWS S3 using aioboto3.
    It implements the singleton pattern for efficient resource usage.
    """

    _instance: Optional["S3Client"] = None
    _lock: Lock = Lock()
    _session: Optional[aioboto3.Session] = None
    _client: Optional[Any] = None
    _initialized: bool = False
    _client_lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls: Type[T]) -> T:
        """Create or return the singleton instance of S3Client."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(S3Client, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance  # type: ignore

    def __init__(self) -> None:
        """Initialize the S3 client with configuration from environment variables."""
        if getattr(self, "_initialized", False):
            return

        # Initialize session
        self._session = aioboto3.Session(
            region_name=os.getenv("S3_AWS_REGION"),
            aws_access_key_id=os.getenv("S3_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_AWS_SECRET_ACCESS_KEY"),
        )
        self._client = None
        self._client_close = None
        self._initialized = True

    @asynccontextmanager
    async def resource(self) -> AsyncGenerator[Any, None]:
        """Async context manager for S3 resource access.

        Yields:
            An aioboto3 S3 resource instance for direct S3 operations.

        Example:
            async with s3.resource() as s3:
                bucket = await s3.Bucket('my-bucket')
                # Perform operations with the bucket
        """
        if self._session is None:
            raise RuntimeError("Session not initialized")
        async with self._session.resource("s3") as s3:
            yield s3

    @property
    @override
    async def client(self) -> Any:
        """Get the S3 client instance.

        Returns:
            aioboto3 S3 client instance for low-level operations.

        Note:
            Prefer using the higher-level methods when possible.
        """
        async with self.resource() as s3:
            return s3.meta.client

    @override
    async def upload_file(
        self, file_path: str, bucket: str, key: str, **kwargs: Any
    ) -> S3Response:
        """Upload a file to an S3 bucket.

        Args:
            file_path: Path to local file to upload
            bucket: Target S3 bucket name
            key: S3 object key/path
            **kwargs: Additional args for boto3 upload_file
                - ExtraArgs: Dict of additional args (e.g., ContentType, ACL)
                - Callback: Progress callback function
                - Config: boto3.s3.transfer.TransferConfig

        Returns:
            Dict with status, bucket, and key

        Raises:
            NoCredentialsError: If AWS credentials are invalid
            ClientError: For S3-specific errors
            FileNotFoundError: If local file doesn't exist
        """
        if not bucket:
            raise ValueError("Bucket name is required")

        try:
            async with self.resource() as s3:
                s3_bucket_obj = await s3.Bucket(bucket)
                await s3_bucket_obj.upload_file(file_path, key)
                return {"status": "success", "bucket": bucket, "key": key}
        except (ClientError, NoCredentialsError) as e:
            logger.error(
                "Failed to upload file %s to s3://%s/%s: %s",
                file_path,
                bucket,
                key,
                str(e),
            )
            raise

    @override
    async def download_file(
        self, bucket: str, key: str, file_path: str, **kwargs: Any
    ) -> bool:
        """Download a file from S3 to local filesystem.

        Args:
            bucket: Source S3 bucket name
            key: S3 object key/path
            file_path: Local path to save file (must include filename)
            **kwargs: Additional args for boto3 download_file
                - ExtraArgs: Additional arguments for download
                - Callback: Progress callback function
                - Config: boto3.s3.transfer.TransferConfig

        Returns:
            bool: True if download was successful

        Raises:
            FileNotFoundError: If file doesn't exist in S3 or local path is invalid
            PermissionError: If permission issues with S3 or local filesystem
            ClientError: For S3-specific errors
            IOError: If issues writing to local filesystem
            ValueError: If bucket name or key is not provided
        """
        try:
            async with self.resource() as s3:
                s3_bucket = await s3.Bucket(bucket)
                await s3_bucket.download_file(key, file_path, **kwargs)
                return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise FileNotFoundError(f"File not found: s3://{bucket}/{key}") from e
            if error_code in ["403", "AccessDenied"]:
                raise PermissionError(
                    f"Access denied to file: s3://{bucket}/{key}"
                ) from e
            raise  # Re-raise other ClientError instances

    @override
    async def delete_object(self, bucket: str, key: str) -> S3Response:
        """Delete an object from S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key to delete

        Returns:
            Dict with operation status and details

        Raises:
            ClientError: If deletion fails
        """
        try:
            async with self.resource() as s3:
                # Use the object's delete method
                obj = await s3.Object(bucket, key)
                response = await obj.delete()

            return {
                "status": "success",
                "bucket": bucket,
                "key": key,
                "response": response,
            }
        except ClientError as e:
            logger.error(f"Error deleting object {key} from bucket {bucket}: {e}")
            raise
        except Exception as e:
            logger.error("Unexpected error in delete_object: %s", str(e))
            raise

    @override
    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        operation: str = "get_object",
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for an S3 object.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            operation: S3 operation ('get_object', 'put_object', etc.)
            expiration: URL expiration time in seconds (default: 1 hour)
            **kwargs: Additional parameters for the S3 operation

        Returns:
            str: Pre-signed URL, or None if credentials are invalid

        Example:
            # Generate upload URL
            url = await s3.generate_presigned_url(
                bucket='my-bucket',
                key='uploads/file.txt',
                operation='put_object',
                ContentType='text/plain'
            )
        """
        try:
            params = {"Bucket": bucket, "Key": key, **kwargs}

            url: str = await (await self.client).generate_presigned_url(
                ClientMethod=operation, Params=params, ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error("Error generating presigned URL: %s", str(e))
            raise

    @override
    async def generate_upload_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for uploading a file to S3.

        This is a convenience wrapper around generate_presigned_url for uploads.

        Args:
            bucket: S3 bucket name
            key: S3 object key where the file will be stored
            expiration: Time in seconds until the URL expires (default: 1 hour)
            **kwargs: Additional parameters to pass to the S3 put_object operation
                Common parameters:
                - ContentType: The content type of the file (e.g., 'image/jpeg')
                - ACL: Access control for the file (e.g., 'private', 'public-read')
                - Metadata: Dictionary of metadata to store with the object

        Returns:
            Optional[str]: The pre-signed URL as a string,
            or None if credentials are invalid

        Example:
            >>> upload_url = await s3.generate_upload_url(
            ...     bucket='my-bucket',
            ...     key='uploads/file.jpg',
            ...     ContentType='image/jpeg',
            ...     ACL='private',
            ...     Metadata={
            ...         'custom': 'value'
            ...     }
            ... )
        """
        # Convert ContentType to proper case if provided
        if "contenttype" in kwargs:
            kwargs["ContentType"] = kwargs.pop("contenttype")

        return await self.generate_presigned_url(
            bucket=bucket,
            key=key,
            operation="put_object",
            expiration=expiration,
            **kwargs,
        )

    @override
    async def generate_download_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for downloading a file from S3.

        This is a convenience wrapper around generate_presigned_url for downloads.

        Args:
            bucket: S3 bucket name
            key: S3 object key of the file to download
            expiration: Time in seconds until the URL expires (default: 1 hour)
            **kwargs: Additional parameters to pass to the S3 get_object operation

        Returns:
            Optional[str]: The pre-signed URL as a string,
            or None if credentials are invalid

        Example:
            >>> download_url = await s3.generate_download_url(
            ...     bucket='my-bucket',
            ...     key='downloads/file.txt',
            ...     ResponseContentType='application/pdf',
            ...     ResponseContentDisposition='attachment; filename=report.pdf'
            ... )
        """
        return await self.generate_presigned_url(
            bucket=bucket,
            key=key,
            operation="get_object",
            expiration=expiration,
            **kwargs,
        )

    @override
    async def upload_string_as_file(
        self, bucket: str, key: str, data: str, **kwargs: Any
    ) -> Optional[str]:
        """Upload a file from a string.

        Args:
            bucket: S3 bucket name
            key: S3 object key where the file will be stored
            data: String of the file contents
            **kwargs: Additional arguments for the upload operation

        Returns:
            Optional[str]: The uploaded file's key, or None if upload fails

        Raises:
            ClientError: If upload fails

        Example:
            >>> await s3.upload_string_as_file(
            ...     bucket='my-bucket',
            ...     key='uploads/file.txt',
            ...     data='file-content'
            ... )
        """
        async with self.resource() as s3:
            client = await s3.Bucket(bucket)
            await client.put_object(Key=key, Body=data, **kwargs)
            return key

    @override
    async def download_as_base64(
        self, bucket: str, key: str, check_exists: bool = True, **kwargs: Any
    ) -> str:
        """Download file from S3 as base64-encoded string.
        This method is useful when you need to work with the file contents
        directly in memory without saving to disk, such as when sending files
        in API responses or processing file contents in memory.

        Args:
            bucket: S3 bucket name
            key: S3 object key
            check_exists: If True, verify file exists first
            **kwargs: Additional args for boto3 get_object
                - VersionId: Version ID of the object
                - SSECustomerAlgorithm: Server-side encryption algorithm
                - SSECustomerKey: Server-side encryption key

        Returns:
            str: Base64-encoded file contents

        Raises:
            FileNotFoundError: If file doesn't exist and check_exists is True
            ClientError: For S3-specific errors

        Note:
            Loads entire file into memory - not suitable for very large files.
        """
        if check_exists and not await self.file_exists(bucket, key):
            raise FileNotFoundError(f"File {key} not found in bucket {bucket}")

        # Download file to in-memory buffer
        buffer = io.BytesIO()
        try:
            async with self.resource() as s3:
                s3_obj = await s3.Object(bucket, key)
                await s3_obj.download_fileobj(buffer, **kwargs)
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode("utf-8")
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                raise FileNotFoundError(
                    f"File {key} not found in bucket {bucket}"
                ) from e
            logger.error(f"Error downloading {key} from {bucket} as base64: {e}")
            raise

    @override
    async def file_exists(self, bucket: str, key: str) -> bool:
        """Check if a file exists in S3.

        Args:
            bucket: S3 bucket name
            key: S3 object key to check

        Returns:
            bool: True if file exists, False otherwise

        Raises:
            ClientError: If error occurs during check
        """
        try:
            async with self.resource() as s3:
                # Use the client directly for head_object
                client = s3.meta.client
                await client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "404":
                return False
            logger.error(f"Error checking if {key} exists in bucket {bucket}: {e}")
            raise ClientError(
                f"Error checking if {key} exists in bucket {bucket}: {e}"
            ) from e
