Database Clients
===============

The database module provides asynchronous database clients for interacting with various database systems.

PostgreSQL Client
----------------

The :class:`~prs_commons.db.postgres.PostgresClient` provides an asynchronous interface for interacting with PostgreSQL databases using ``asyncpg``.

Environment Variables
--------------------

The PostgreSQL client can be configured using the following environment variables:

- ``DB_HOST``: Database host (default: localhost)
- ``DB_PORT``: Database port (default: 5432)
- ``DB_NAME``: Database name (default: postgres)
- ``DB_USER``: Database user (required)
- ``DB_PASSWORD``: Database password (required)
Example ``.env`` file:

.. code-block:: bash

   # Either use individual components
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=mydb
   DB_USER=myuser
   DB_PASSWORD=mypassword

Basic Usage
-----------

.. code-block:: python

   from prs_commons.db import PostgresClient
   import asyncio
   import os

   async def main():
       # Create a client with connection pooling
       client = PostgresClient()
       
       # Connect to the database
       await client.connect()
       
       try:
           # Execute a query
           result = await client.fetch_one("SELECT * FROM users WHERE id = $1", 1)
           print(f"User: {result}")
           
           # Use transaction
           async with client.connection() as conn:
               await conn.execute("UPDATE users SET last_login = NOW() WHERE id = $1", 1)
               # Transaction will be committed when the block exits
               
       finally:
           # Close the connection pool
           await client.disconnect()

   if __name__ == "__main__":
       asyncio.run(main())

API Reference
------------

.. autoclass:: prs_commons.db.postgres.PostgresClient
   :members:
   :inherited-members:
   :special-members: __aenter__, __aexit__
   :exclude-members: __new__

   .. automethod:: __init__(dsn=None, min_size=1, max_size=50, **kwargs)
      :noindex:

Error Handling
-------------

The client raises the following exceptions:

- :exc:`ValueError`: If required environment variables are missing
- :exc:`asyncpg.PostgresError`: For database-related errors
- :exc:`Exception`: For other unexpected errors

See Also
--------
- `asyncpg Documentation <https://magicstack.github.io/asyncpg/current/>`_
- `PostgreSQL Documentation <https://www.postgresql.org/docs/>`_
