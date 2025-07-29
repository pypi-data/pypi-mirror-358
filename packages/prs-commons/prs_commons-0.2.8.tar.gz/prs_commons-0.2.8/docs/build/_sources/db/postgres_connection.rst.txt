Postgres Connection
===============

The database module provides asynchronous database clients with connection pooling and transaction management for various database systems.

Environment Variables
---------------------

The PostgreSQL client can be configured using either a connection string or individual environment variables:
The PostgreSQL client can be configured using the following environment variables:

- ``DB_HOST``: Database host (default: localhost)
- ``DB_PORT``: Database port (default: 5432)
- ``DB_NAME``: Database name (default: postgres)
- ``DB_USER``: Database user (required)
- ``DB_PASSWORD``: Database password (required)
- ``DB_SSLMODE``: SSL mode (default: disable)

Example ``.env`` file:

.. code-block:: bash

    # Database configuration
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=mydb
    DB_USER=myuser
    DB_PASSWORD=mypassword
    DB_SSLMODE=disable

API Reference
-------------

.. autoclass:: prs_commons.db.PostgresConnection
   :members:
   :special-members: __aenter__, __aexit__
   :exclude-members: __new__

   The :class:`~prs_commons.db.PostgresConnection` manages the actual database connections and connection pooling. It's typically not used directly but rather through the higher-level :class:`~prs_commons.db.PostgresClient`.

   .. automethod:: __init__(dsn=None, min_size=1, max_size=50, **kwargs)
      :noindex:

   .. automethod:: connect()
      :async:
      Establish the connection pool. Called automatically on first use.

   .. automethod:: disconnect()
      :async:
      Close all connections in the pool.

   .. automethod:: connection()
      :async-for:
      Get a connection from the pool with automatic transaction management.

   .. automethod:: get_pool()
      :async:
      Get the underlying connection pool (use with caution).

   .. automethod:: is_connected()
      Check if the connection pool is initialized.

Error Handling
--------------

The :class:`~prs_commons.db.postgres.PostgresConnection` raises the following exceptions:

- :exc:`ValueError`: If required environment variables are missing
- :exc:`asyncpg.PostgresError`: For database-related errors
- :exc:`RuntimeError`: For connection pool errors
- :exc:`Exception`: For other unexpected errors

See Also
--------
- `asyncpg Documentation <https://magicstack.github.io/asyncpg/current/>`_
- `PostgreSQL Documentation <https://www.postgresql.org/docs/>`_
- `Connection Pooling <https://magicstack.github.io/asyncpg/current/api/index.html#connection-pools>`_
