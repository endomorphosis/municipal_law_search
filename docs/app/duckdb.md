# duckdb.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/api/database/implementations/duckdb.py`

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

- [`execute_sql_query`](#duckdbclientexecute_sql_query)

### `execute_sql_query`

```python
def execute_sql_query(self, query)
```

Execute a SQL query against the DuckDB database.

**Parameters:**

- `query` (`str`): SQL query string

**Returns:**

- `List[Dict[(str, Any)]]`: List of dictionaries representing the query results
