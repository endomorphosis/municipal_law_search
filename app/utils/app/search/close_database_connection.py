
"""
Utility module for safely closing database connections.

This module provides a function to safely close a database connection,
with appropriate logging, to prevent resource leaks.
"""
from .type_vars import SqlConnection
from app import logger


def close_database_connection(connection: SqlConnection | None) -> None:
    """Safely close a database connection if one is present."""
    if connection is None:
        return
    else:
        connection.close()
        logger.info("Closed database connection.")
