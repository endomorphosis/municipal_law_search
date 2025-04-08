
"""
Utility module for safely closing database connections.

This module provides a function to safely close a database connection,
with appropriate logging, to prevent resource leaks.
"""
from .type_vars import SqlConnection
from app import logger


def close_database_connection(connection: SqlConnection | None) -> None:
    """
    Safely closes a database connection and logs the action.
    
    This function checks if the connection is not None before attempting to close it,
    and logs an info message when the connection is successfully closed. If the
    connection is None, the function returns without doing anything.
    
    The algorithm:
    1. Check if the connection exists (is not None)
    2. If it does not exist, return without action
    3. If it exists, close the connection
    4. Log an info message confirming the connection was closed
    
    Args:
        connection: The database connection to close, can be None
        
    Returns:
        None
        
    Example:
        ```python
        # Get a database connection
        connection = get_american_law_db()
        try:
            # Use the connection for database operations
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM citations")
        finally:
            # Always close the connection when done
            close_database_connection(connection)
        ```
    """
    if connection is None:
        return
    else:
        connection.close()
        logger.info("Closed database connection.")
