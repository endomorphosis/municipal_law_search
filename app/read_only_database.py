"""
A module to manage the database connection and operations.
This module provides a singleton instance of the Database class, which is read-only by default.
"""
from configs import configs
from api_.database import Database
from api_.database.dependencies.duckdb_database import DuckDbDatabase


# Export resources dictionary for use with Database class
duckdb_resources = {
    "begin": DuckDbDatabase.begin,
    "close": DuckDbDatabase.close,
    "commit": DuckDbDatabase.commit,
    "connect": DuckDbDatabase.connect,
    "create_function": DuckDbDatabase.create_function,
    "create_index_if_not_exists": DuckDbDatabase.create_index_if_not_exists,
    "create_table_if_not_exists": DuckDbDatabase.create_table_if_not_exists,
    "execute": DuckDbDatabase.execute,
    "fetch": DuckDbDatabase.fetch,
    "fetch_all": DuckDbDatabase.fetch_all,
    "fetch_one": DuckDbDatabase.fetch,
    "get_cursor": DuckDbDatabase.get_cursor,
    "rollback": DuckDbDatabase.rollback,
    "read_only": True,  # Set read_only to True for read-only access
}

# Initialize the singleton database instance with DuckDB resources.
READ_ONLY_DB = None
READ_ONLY_DB = Database(configs=configs, resources=duckdb_resources)

# Close the database connection when the program is terminated.
def close_db_connection():
    if READ_ONLY_DB is not None:
        READ_ONLY_DB.exit()
        print("Database connection closed.")

import atexit # NOTE: Huh, who knew?
atexit.register(close_db_connection)