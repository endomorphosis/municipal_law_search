"""
A module to manage the database connection and operations.
This module provides a singleton instance of the Database class, which is read-only by default.
"""
from typing import Callable


from configs import configs as project_configs, Configs
from logger import logger as  module_logger
from api_.database import Database
from api_.database.dependencies.duckdb_database import DuckDbDatabase



def make_read_only_db(mock_resources: dict[str, Callable] = None, mock_configs: Configs = None) -> Database:
    """
    Factory function to create a new Database instance.
    
    This function initializes a new Database object with the provided configurations
    and DuckDB resources. It is intended to be used for creating database connections
    as needed.

    Args:
        mock_resources (dict[str, Any], optional): A dictionary of callables to override injected defaults. Defaults to None.
        mock_configs (Configs, optional): A Configs object to override default configurations. Defaults to None.

    Returns:
        Database: A new instance of the Database class.
    """
    # Export resources dictionary for use with Database class
    configs = mock_configs or project_configs
    _resources = mock_resources or {}

    duckdb_resources = {
        "begin": _resources.pop("begin", DuckDbDatabase.begin),
        "close": _resources.pop("close", DuckDbDatabase.close),
        "commit": _resources.pop("commit", DuckDbDatabase.commit),
        "connect": _resources.pop("connect", DuckDbDatabase.connect),
        "create_function": _resources.pop("create_function", DuckDbDatabase.create_function),
        "create_index_if_not_exists": _resources.pop("create_index_if_not_exists", DuckDbDatabase.create_index_if_not_exists),
        "create_table_if_not_exists": _resources.pop("create_table_if_not_exists", DuckDbDatabase.create_table_if_not_exists),
        "execute": _resources.pop("execute", DuckDbDatabase.execute),
        "fetch": _resources.pop("fetch", DuckDbDatabase.fetch),
        "fetch_all": _resources.pop("fetch_all", DuckDbDatabase.fetch_all),
        "fetch_one": _resources.pop("fetch_one", DuckDbDatabase.fetch),
        "get_cursor": _resources.pop("get_cursor", DuckDbDatabase.get_cursor),
        "rollback": _resources.pop("rollback", DuckDbDatabase.rollback),
        "read_only": _resources.pop("read_only", True),  # Set read_only to True for read-only access
        "logger": _resources.pop("logger", module_logger),
    }

    for key in _resources.keys():
        if key not in duckdb_resources:
            raise KeyError(f"Unexpected resource key: {key}")

    return Database(configs=configs, resources=duckdb_resources)


# Initialize the singleton database instance with DuckDB resources.
READ_ONLY_DB = None
READ_ONLY_DB = make_read_only_db()

# Close the database connection when the program is terminated.
def close_db_connection():
    if READ_ONLY_DB is not None:
        READ_ONLY_DB.exit()
        print("Database connection closed.")

import atexit # NOTE: Huh, who knew?
atexit.register(close_db_connection)