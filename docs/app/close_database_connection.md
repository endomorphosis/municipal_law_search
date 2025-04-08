# close_database_connection.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/close_database_connection.py`

## Module Description

Utility module for safely closing database connections.

This module provides a function to safely close a database connection,
with appropriate logging, to prevent resource leaks.

## Table of Contents

### Functions

- [`close_database_connection`](#close_database_connection)

## Functions

## `close_database_connection`

```python
def close_database_connection(connection)
```

Safely closes a database connection and logs the action.

This function checks if the connection is not None before attempting to close it,
and logs an info message when the connection is successfully closed. If the
connection is None, the function returns without doing anything.

**Parameters:**

- `connection` (`SqlConnection | None`): The database connection to close, can be None

**Returns:**

- `None`: None

**Examples:**

```python
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
```
