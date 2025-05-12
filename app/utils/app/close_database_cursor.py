"""
Utility module for safely closing database cursors.

This module provides a function to safely close a database cursor,
with appropriate logging, to prevent resource leaks.
"""
from utils.app.search.type_vars import SqlCursor


from logger import logger


def close_database_cursor(cursor: SqlCursor) -> None:
    """
    Close a database cursor.

    Args:
        cursor: The database cursor to close

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