Storage Module
==============

The storage module provides a unified interface for interacting with different storage backends. It defines a base `StorageClient` class that can be implemented by specific storage providers.

Base Storage Interface
---------------------

The `StorageClient` abstract base class defines the common interface that all storage clients must implement.

.. autoclass:: prs_commons.storage.base.StorageClient
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: __weakref__

Available Implementations
-----------------------

- :doc:`AWS S3 Client <aws>` - For interacting with Amazon S3 storage

Creating a Custom Storage Client
------------------------------

To create a custom storage client, inherit from the `StorageClient` base class and implement all required methods:

.. code-block:: python

   from prs_commons.storage.base import StorageClient

   class CustomStorageClient(StorageClient):
       def __init__(self, connection_string: str):
           self.connection_string = connection_string
           self._client = self._initialize_client()

       @property
       def client(self) -> Any:
           """Return the underlying client instance."""
           return self._client

       def upload_file(
           self, file_path: str, bucket: str, key: str, **kwargs: Any
       ) -> Dict[str, Any]:
           # Implementation here
           pass

       # Implement other required methods...


   # Usage
   storage = CustomStorageClient("your-connection-string")
   storage.upload_file("local.txt", "bucket", "remote.txt")
