# duckdb_database.py: last updated 03:23 PM on May 06, 2025

**File Path:** `app/api/database/dependencies/duckdb_database.py`

## Module Description

DuckDB-specific implementation for the Database class.

This module provides DuckDB-specific implementations of database operations
for use with the Database class through dependency injection.

## Table of Contents

### Classes

- [`DuckDbDatabase`](#duckdbdatabase)

## Classes

## `DuckDbDatabase`

```python
class DuckDbDatabase(object)
```

DuckDB-specific implementation of database operations.

This class provides static methods that implement DuckDB-specific
database operations for use with the Database class.

**Methods:**

- [`close`](#close) (static method)
- [`commit`](#commit) (static method)
- [`connect`](#connect) (static method)
- [`create_function`](#create_function) (static method)
- [`create_index_if_not_exists`](#create_index_if_not_exists) (static method)
- [`create_table_if_not_exists`](#create_table_if_not_exists) (static method)
- [`execute`](#execute) (static method)
- [`execute_script`](#execute_script) (static method)
- [`fetch_all`](#fetch_all) (static method)
- [`get_cursor`](#get_cursor) (static method)
- [`get_session`](#get_session) (static method)
- [`rollback`](#rollback) (static method)

### `close`

```python
@staticmethod
def close(conn)
```

Close a DuckDB connection.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection to close

### `commit`

```python
@staticmethod
def commit(conn)
```

Commit the current transaction.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

**Raises:**

- `Exception`: If commit fails

### `connect`

```python
@staticmethod
def connect(db_path=None, read_only=True)
```

Connect to a DuckDB database.

**Parameters:**

- `db_path` (`Optional[str]`): Path to the DuckDB database file, or None to use in-memory database

- `read_only` (`bool`): Whether to open the database in read-only mode

**Returns:**

- `duckdb.DuckDBPyConnection`: A DuckDB connection

**Raises:**

- `Exception`: If connection fails

### `create_function`

```python
@staticmethod
def create_function(conn, name, function, argument_types=None, return_type=None)
```

Register a Python function with DuckDB.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

- `name` (`str`): Name to register the function as

- `function` (`callable`): The Python function to register

- `argument_types` (`List`): List of argument types

- `return_type` (`Optional[Any]`): Return type of the function

**Raises:**

- `Exception`: If function registration fails

### `create_index_if_not_exists`

```python
@staticmethod
def create_index_if_not_exists(conn, table_name, index_name, columns, unique=False)
```

Create an index if it doesn't exist.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

- `table_name` (`str`): Name of the table to create the index on

- `index_name` (`str`): Name of the index to create

- `columns` (`List[str]`): List of column names to include in the index

- `unique` (`bool`): Whether the index should enforce uniqueness

**Raises:**

- `Exception`: If index creation fails

### `create_table_if_not_exists`

```python
@staticmethod
def create_table_if_not_exists(conn, table_name, columns, constraints=None)
```

Create a table if it doesn't exist.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

- `table_name` (`str`): Name of the table to create

- `columns` (`List[Dict[(str, str)]]`): List of column definitions, each a dict with 'name' and 'type'

- `constraints` (`Optional[List[str]]`): Optional list of constraint definitions

**Raises:**

- `Exception`: If table creation fails

### `execute`

```python
@staticmethod
def execute(conn, query, params=None)
```

Execute a query on a DuckDB connection.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

- `query` (`str`): The SQL query to execute

- `params` (`Optional[Union[(Tuple, Dict[(str, Any)])]]`): Optional parameters for the query

**Returns:**

- `Any`: The cursor after executing the query

**Raises:**

- `Exception`: If query execution fails

### `execute_script`

```python
@staticmethod
def execute_script(conn, script)
```

Execute a multi-statement SQL script.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

- `script` (`str`): The SQL script to execute

**Raises:**

- `Exception`: If script execution fails

### `fetch_all`

```python
@staticmethod
def fetch_all(conn, query, params=None, return_format='records')
```

Fetch all results from a query.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

- `query` (`str`): The SQL query to execute

- `params` (`Optional[Union[(Tuple, Dict[(str, Any)])]]`): Optional parameters for the query

- `return_format` (`Optional[str]`): Format for the returned data, one of 'records', 'dict', 'list'

**Returns:**

- `List[Dict[(str, Any)]]`: Query results in the specified format

**Raises:**

- `Exception`: If query execution fails

### `get_cursor`

```python
@staticmethod
def get_cursor(conn)
```

Get a cursor from a DuckDB connection.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

**Returns:**

- `Any`: A DuckDB cursor

### `get_session`

```python
@staticmethod
def get_session(conn)
```

Get a session from a DuckDB connection.

Note: DuckDB doesn't have a separate session concept like SQLAlchemy,
so this just returns the connection itself.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

**Returns:**

- `Any`: The connection object (DuckDB doesn't have separate sessions)

### `rollback`

```python
@staticmethod
def rollback(conn)
```

Rollback the current transaction.

**Parameters:**

- `conn` (`duckdb.DuckDBPyConnection`): The DuckDB connection

**Raises:**

- `Exception`: If rollback fails
