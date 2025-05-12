# duckdb.py: last updated 03:23 PM on May 06, 2025

**File Path:** `app/api/database/dependencies/duckdb.py`

## Table of Contents

### Classes

- [`DuckDbClient`](#duckdbclient)

## Classes

## `DuckDbClient`

```python
class DuckDbClient(object)
```

**Constructor Parameters:**

- `db_path` (`Any`): Path to the DuckDB database file

**Methods:**

- [`execute_sql_query`](#execute_sql_query)

### `execute_sql_query`

```python
def execute_sql_query(self, query)
```

Execute a SQL query against the DuckDB database.

**Parameters:**

- `query` (`str`): SQL query string

**Returns:**

- `List[Dict[(str, Any)]]`: List of dictionaries representing the query results
