# close_database_cursor.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/close_database_cursor.py`

## Module Description

Utility module for safely closing database cursors.

This module provides a function to safely close a database cursor,
with appropriate logging, to prevent resource leaks.

## Table of Contents

### Functions

- [`close_database_cursor`](#close_database_cursor)

## Functions

## `close_database_cursor`

```python
def close_database_cursor(cursor)
```

Safely closes a database cursor and logs the action.

This function checks if the cursor is not None before attempting to close it,
and logs a debug message when the cursor is successfully closed.

**Parameters:**

- `cursor` (`SqlCursor`): The database cursor to close

**Returns:**

- `None`: None

**Examples:**

```python
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
```
