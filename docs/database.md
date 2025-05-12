# database.py: last updated 03:23 PM on May 06, 2025

**File Path:** `app/api/database/database.py`

## Module Description

Database connection and session management for the FastAPI application.

This module provides a Database class that encapsulates database connection management,
connection pooling, and CRUD operations. It supports multiple database engines
through a dependency injection pattern.

## Table of Contents

### Classes

- [`Database`](#database)

## Classes

## `Database`

```python
class Database(object)
```

A class to manage database connections and operations.

This class provides methods for database connection management,
connection pooling, and CRUD operations. It's designed to work
with multiple database engines through dependency injection.

**Constructor Parameters:**

- `configs` (`Optional[Configs]`): Configuration settings for the database
- `resources` (`Optional[Dict[(str, Callable)]]`): Dictionary of callable functions for database operations

**Methods:**

- [`_get_connection_from_pool`](#_get_connection_from_pool)
- [`_init_connection_pool`](#_init_connection_pool)
- [`_return_connection_to_pool`](#_return_connection_to_pool)
- [`close`](#close)
- [`commit`](#commit)
- [`connect`](#connect)
- [`cursor`](#cursor)
- [`execute`](#execute)
- [`fetch_all`](#fetch_all)
- [`get_session`](#get_session)
- [`rollback`](#rollback)
- [`transaction`](#transaction)

**Special Methods:**

- [`__enter__`](#__enter__)
- [`__exit__`](#__exit__)

### `_get_connection_from_pool`

```python
def _get_connection_from_pool(self)
```

Get a connection from the pool or create a new one if needed.

**Returns:**

- `Tuple[(Any, bool)]`: - The database connection
        - Boolean indicating if a new connection was created

### `_init_connection_pool`

```python
def _init_connection_pool(self)
```

Initialize the connection pool with a set of database connections.

This method creates new connections and adds them to the connection pool
up to the maximum pool size defined in configuration.

### `_return_connection_to_pool`

```python
def _return_connection_to_pool(self, conn)
```

Return a connection to the pool if space is available.

**Parameters:**

- `conn` (`Any`): The database connection to return to the pool

### `close`

```python
def close(self)
```

Close or return the current database connection to the pool.

### `commit`

```python
def commit(self)
```

Commit the current transaction.

**Raises:**

- `Exception`: If no database connection is established

### `connect`

```python
def connect(self)
```

Establish a connection to the database.

This method gets a connection from the pool or creates a new one.

### `cursor`

```python
def cursor(self)
```

Get a cursor for the database connection.

**Returns:**

- `Any`: A database cursor

**Raises:**

- `Exception`: If no database connection is established

### `execute`

```python
def execute(self, query, params=None)
```

Execute a database query.

**Parameters:**

- `query` (`str`): The SQL query to execute

- `params` (`Optional[Tuple | Dict[str, Any]]`): Optional parameters for the query

**Returns:**

- `Any`: The result of the query execution

**Raises:**

- `Exception`: If no database connection is established

### `fetch_all`

```python
def fetch_all(self, query, params=None, return_format=None)
```

Fetch all results from a query.

**Parameters:**

- `query` (`str`): The SQL query to execute

- `params` (`Optional[Tuple | Dict[str, Any]]`): Optional parameters for the query

- `return_format` (`Optional[str]`): Optional format for the return value

**Returns:**

- `List[Dict[(str, Any)]]`: A list of results as dictionaries

**Raises:**

- `Exception`: If no database connection is established

### `get_session`

```python
def get_session(self)
```

Get a new session for database operations.

**Returns:**

- `Any`: A database session

### `rollback`

```python
def rollback(self)
```

Rollback the current transaction.

**Raises:**

- `Exception`: If no database connection is established

### `transaction`

```python
def transaction(self)
```

Transaction context manager.

**Returns:**

- `Any`: A context manager for transaction handling

### `__enter__`

```python
def __enter__(self)
```

Context manager entry method.

**Returns:**

- `Database`: The database instance

### `__exit__`

```python
def __exit__(self, exc_type, exc_val, exc_tb)
```

Context manager exit method.

**Parameters:**

- `exc_type` (`Any`): Exception type if an exception was raised

- `exc_val` (`Any`): Exception value if an exception was raised

- `exc_tb` (`Any`): Exception traceback if an exception was raised
