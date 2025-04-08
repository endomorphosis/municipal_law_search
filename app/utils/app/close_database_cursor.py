"""
Utility module for safely closing database cursors.

This module provides a function to safely close a database cursor,
with appropriate logging, to prevent resource leaks.
"""
from app.utils.app.search.type_vars import SqlCursor


from app import logger


def close_database_cursor(cursor: SqlCursor) -> None:
    """
    Safely closes a database cursor and logs the action.
    
    This function checks if the cursor is not None before attempting to close it,
    and logs a debug message when the cursor is successfully closed.
    
    The algorithm:
    1. Check if the cursor exists (is not None)
    2. If it exists, close it
    3. Log a debug message confirming the cursor was closed
    
    Args:
        cursor: The database cursor to close
        
    Returns:
        None
        
    Example:
        ```python
        cursor = get_a_database_connection()
        try:
            # Execute some queries with the cursor
            cursor.execute("SELECT * FROM citations")
            results = cursor.fetchall()
        finally:
            # Always close the cursor when done
            close_database_cursor(cursor)
        ```
    """
    if cursor:
        cursor.close()
        logger.debug("Database cursor closed.")