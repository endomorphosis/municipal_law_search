# Database Module

This module provides a Database class for managing database connections and operations with connection pooling, transaction management, and error handling.

## Overview

The Database module includes:

1. A generic `Database` class that manages database connections and operations through dependency injection
2. A DuckDB-specific implementation of database operations
3. Connection pooling for improved performance under load
4. Transaction management via a context manager
5. Comprehensive error handling and logging

## Usage Examples

### Basic Usage

```python
from app.api.database.database import db

# Using the singleton database instance
with db:
    # Execute a query
    results = db.fetch_all("SELECT * FROM users WHERE id = ?", (user_id,))
    
    # Process results
    for row in results:
        print(row["name"])
```

### Transaction Management

```python
from app.api.database.database import db

# Using the transaction context manager
with db.transaction():
    # These operations will be committed if successful or rolled back if an exception occurs
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
    db.execute("UPDATE user_counts SET count = count + 1")
```

### Multiple Queries

```python
from app.api.database.database import db

with db:
    # Execute multiple queries with proper parameter binding
    db.execute("INSERT INTO search_history (query, timestamp) VALUES (?, ?)", 
              (search_query, current_timestamp))
              
    # Fetch data
    results = db.fetch_all("""
        SELECT * FROM search_history 
        WHERE client_id = ? 
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """, (client_id, limit, offset))
```

### Table and Index Creation

```python
from app.api.database.database import db
from app.api.database.dependencies.duckdb_database import DuckDbDatabase

with db:
    # Create a table
    DuckDbDatabase.create_table_if_not_exists(
        db.connection,
        "search_history",
        [
            {"name": "search_history_cid", "type": "VARCHAR PRIMARY KEY"},
            {"name": "search_query", "type": "TEXT NOT NULL"},
            {"name": "client_id", "type": "VARCHAR NOT NULL"},
            {"name": "timestamp", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
            {"name": "result_count", "type": "INTEGER NOT NULL"}
        ]
    )
    
    # Create an index
    DuckDbDatabase.create_index_if_not_exists(
        db.connection,
        "search_history",
        "idx_search_history_client_id",
        ["client_id"]
    )
```

### Custom SQL Functions

```python
from app.api.database.database import db
from app.api.database.dependencies.duckdb_database import DuckDbDatabase
from datetime import datetime

# Define a function to register with DuckDB
def get_datetime_iso_format() -> str:
    return datetime.now().isoformat()

with db:
    # Register the function with DuckDB
    DuckDbDatabase.create_function(
        db.connection,
        "get_datetime_iso_format",
        get_datetime_iso_format,
        [],
        "TIMESTAMP"
    )
    
    # Use the function in a query
    db.execute("""
        INSERT INTO search_history (
            search_history_cid,
            search_query,
            client_id,
            timestamp
        ) VALUES (?, ?, ?, get_datetime_iso_format())
    """, (cid, query, client_id))
```

## Architecture

The Database module is designed with a dependency injection pattern to support multiple database engines:

1. The `Database` class provides the core interface for database operations
2. Engine-specific implementations provide the actual database operations
3. The `resources` dictionary maps function names to implementation functions
4. The singleton `db` instance is initialized with the DuckDB implementation

This architecture allows for easy switching between database engines (e.g., DuckDB, SQLite) by providing different sets of resource functions.

## Error Handling

The module includes comprehensive error handling:

1. All database operations are wrapped in try-except blocks
2. Errors are logged with appropriate levels
3. Connection cleanup is performed even if errors occur
4. Transactions are automatically rolled back on error

## Connection Pooling

The module implements connection pooling for improved performance:

1. Connections are created and added to a pool at initialization
2. Connections are reused from the pool when available
3. Connections are returned to the pool when no longer needed
4. Aged connections are automatically closed and new ones created
5. Thread safety is maintained with locks

## Best Practices

When using the Database module:

1. Always use the context manager pattern (with db:) to ensure proper cleanup
2. Use parameter binding instead of string concatenation to prevent SQL injection
3. Use transactions for operations that need to be atomic
4. Use the proper return format for your needs (records, dict, or list)
5. Check for errors and handle them appropriately