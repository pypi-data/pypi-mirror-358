PostgresClient
==============

The PostgresClient provides a high-level interface for executing database queries and commands.

.. currentmodule:: prs_commons.db

API Reference
-------------

.. autoclass:: PostgresClient
   :members:
   :special-members: __aenter__, __aexit__
   :exclude-members: __new__

   The PostgresClient provides a high-level interface for executing database queries and commands.

   **Example Usage**::

      from prs_commons.db.postgres import PostgresConnection, PostgresClient
      import asyncio

      async def main():
          # Initialize connection manager
          db_conn = PostgresConnection()
          await db_conn.connect()

          # Initialize client
          db = PostgresClient()

          # Use a connection
          async with db_conn.get_connection() as conn:
              # Fetch a single row
              user = await db.fetch_one(
                  conn,
                  "SELECT * FROM users WHERE id = $1",
                  1
              )
              print(f"User: {user}")

              # Execute an update
              success, result = await db.execute(
                  conn,
                  "UPDATE users SET last_login = NOW() WHERE id = $1 RETURNING id",
                  1
              )
              if success:
                  print(f"Updated user ID: {result}")


      if __name__ == "__main__":
          asyncio.run(main())

Error Handling
--------------

The client raises the following exceptions:

- :exc:`ValueError`: If required environment variables are missing
- :exc:`asyncpg.PostgresError`: For database-related errors
- :exc:`RuntimeError`: For connection or db state errors
- :exc:`Exception`: For other unexpected errors

See Also
--------
- `asyncpg Documentation <https://magicstack.github.io/asyncpg/>`_
- `PostgreSQL Documentation <https://www.postgresql.org/docs/>`_
