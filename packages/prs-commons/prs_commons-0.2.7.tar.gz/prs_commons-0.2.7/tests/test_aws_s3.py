"""Tests for AWS S3 client functionality with async support."""

import base64
import hashlib
import os
import tempfile
from pathlib import Path

import pytest
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from prs_commons.aws.s3_client import S3Client

# Configure pytest
pytestmark = pytest.mark.asyncio

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Test configuration
TEST_BUCKET = os.getenv("S3_BUCKET_NAME")
TEST_PREFIX = "test-prs-commons/"
TEST_FILE_CONTENT = b"This is a test file for S3 client testing"


class TestS3Client:
    """Test cases for S3Client."""

    @pytest.fixture(autouse=True)
    def setup_test(self):
        """Set up for each test - create S3Client instance and test files list."""
        if not TEST_BUCKET:
            pytest.skip("S3_BUCKET_NAME environment variable not set")
        self.s3 = S3Client()
        self.test_files = []

    @pytest.fixture(autouse=True)
    def cleanup_test(self):
        """Clean up test files after each test."""
        yield
        # Cleanup handled in teardown_method
        self.teardown_method()

    async def teardown_method(self):
        """Clean up test files after each test method."""
        if not hasattr(self, "test_files") or not self.test_files:
            return

        for key in self.test_files[:]:
            try:
                await self.s3.delete_object(bucket=TEST_BUCKET, key=key)
            except Exception:
                continue
            self.test_files.remove(key)

    async def test_upload_download_file_WithValidFile_ShouldSucceed(self):
        """Test uploading and downloading a file."""
        # Create a temporary file for upload
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(TEST_FILE_CONTENT)
            temp_file_path = temp_file.name

        # Create a temporary file for download
        download_path = temp_file_path + ".download"

        try:
            # Upload the file
            key = f"{TEST_PREFIX}upload_download_test.txt"
            self.test_files.append(key)
            result = await self.s3.upload_file(
                file_path=temp_file_path,
                key=key,
                bucket=TEST_BUCKET,
                content_type="application/octet-stream",
            )
            assert result["status"] == "success", "Upload should succeed"

            # Verify file exists in S3
            exists = await self.s3.file_exists(bucket=TEST_BUCKET, key=key)
            assert exists, "File should exist in S3"

            # Download the file
            result = await self.s3.download_file(
                key=key, bucket=TEST_BUCKET, file_path=download_path
            )
            assert result is True, "Download should succeed"

            # Verify the downloaded content matches
            with open(download_path, "rb") as f:
                content = f.read()
            assert content == TEST_FILE_CONTENT, "Downloaded content doesn't match"
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(download_path):
                os.unlink(download_path)

    async def test_upload_download_delete_WithExistingFile_ShouldSucceed(self):
        """Test uploading a string and downloading it as base64."""
        # Prepare test data
        test_content = "Test string content for upload and download"
        hash_value = hashlib.sha1(test_content.encode("utf-8")).hexdigest()
        key = TEST_PREFIX + hash_value
        self.test_files.append(key)  # Ensure cleanup

        # Upload the string directly
        uploaded_key = await self.s3.upload_string_as_file(
            bucket=TEST_BUCKET,
            key=key,
            data=test_content,  # Plain text, not base64-encoded
            ContentType="text/plain",
        )
        assert uploaded_key == key, "Upload should return the correct key"

        # Verify file exists
        exists = await self.s3.file_exists(bucket=TEST_BUCKET, key=key)
        assert exists is True, "File should exist in S3 after upload"

        # Download as base64 and verify content
        downloaded_base64 = await self.s3.download_as_base64(
            bucket=TEST_BUCKET, key=key
        )

        # The downloaded content should be base64-encoded
        # Decode it and compare with original
        decoded_content = base64.b64decode(downloaded_base64).decode("utf-8")
        assert decoded_content == test_content, "Decoded content doesn't match original"

        # Delete the file using our async method
        result = await self.s3.delete_object(bucket=TEST_BUCKET, key=key)
        assert (
            result.get("status") == "success"
        ), "Delete operation should be successful"

        # Verify the file does not exist using the resource
        exists = await self.s3.file_exists(bucket=TEST_BUCKET, key=key)
        assert exists is False, "File should not exist after deletion"
        assert (
            result.get("status") == "success"
        ), f"Delete operation should be successful, got: {result}"

        # Verify the file is deleted
        with pytest.raises(ClientError) as exc_info:
            async with self.s3.resource() as s3:
                client = s3.meta.client
                await client.head_object(Bucket=TEST_BUCKET, Key=key)
        assert (
            exc_info.value.response["Error"]["Code"] == "404"
        ), "File should be deleted"

    async def test_download_as_base64_WithNonExistentFile_ShouldRaiseFileNotFound(self):
        """Test that FileNotFoundError is
        raised when trying to download non-existent file."""
        key = f"{TEST_PREFIX}non_existent_file.txt"

        # Try to download a non-existent file - should
        # raise ClientError with code NoSuchKey
        # which is converted to FileNotFoundError in the S3Client implementation
        with pytest.raises(FileNotFoundError) as excinfo:
            await self.s3.download_as_base64(bucket=TEST_BUCKET, key=key)

        assert (
            "not found" in str(excinfo.value).lower()
        ), "Should raise FileNotFoundError"

    async def test_upload_via_presigned_url_WithValidFile_ShouldUploadAndDownloadSuccessfully(  # noqa: E501
        self,
    ):
        """Test uploading and downloading via presigned URL."""
        # Generate a presigned URL for upload
        key = f"{TEST_PREFIX}presigned_upload.txt"
        upload_url = await self.s3.generate_upload_url(
            bucket=TEST_BUCKET, key=key, ContentType="text/plain"
        )
        self.test_files.append(key)

        # Upload file using the presigned URL
        response = requests.put(
            upload_url,
            data=TEST_FILE_CONTENT,
            headers={"Content-Type": "text/plain"},
            timeout=30,
        )
        assert (
            response.status_code == 200
        ), f"Upload failed with status {response.status_code}"

        # Generate a presigned URL for download
        download_url = await self.s3.generate_presigned_url(
            bucket=TEST_BUCKET, key=key, ResponseContentType="text/plain"
        )

        # Download the file using the presigned URL
        response = requests.get(download_url, timeout=30)
        assert (
            response.status_code == 200
        ), f"Download failed with status {response.status_code}"
        assert response.content == TEST_FILE_CONTENT, "Downloaded content doesn't match"

        # Verify the file exists and has the correct content type
        async with self.s3.resource() as s3:
            # Use the client directly for head_object
            client = s3.meta.client
            head = await client.head_object(Bucket=TEST_BUCKET, Key=key)
            assert (
                head["ResponseMetadata"]["HTTPStatusCode"] == 200
            ), "File should exist in S3"
            # Content type can be either text/plain or
            # binary/octet-stream depending on S3 implementation
            assert head.get("ContentType") in [
                "text/plain",
                "binary/octet-stream",
            ], f"""Content type should be 'text/plain' or
            'binary/octet-stream' but was {head.get('ContentType')}"""
