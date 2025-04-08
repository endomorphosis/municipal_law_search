# get_db.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/database/get_db.py`

## Table of Contents

### Functions

- [`_get_db`](#_get_db)
- [`get_citation_db`](#get_citation_db)
- [`get_html_db`](#get_html_db)
- [`get_embeddings_db`](#get_embeddings_db)
- [`get_american_law_db`](#get_american_law_db)

## Functions

## `_get_db`

```python
def _get_db(db_path, use_duckdb, read_only)
```

Get a database connection.

**Parameters:**

- `db_path` (`str`): Path to the database file
use_duckdb: Whether to use DuckDB (True) or SQLite (False)

**Returns:**

- `sqlite3.Connection | duckdb.DuckDBPyConnection`: Database connection object

## `get_citation_db`

```python
def get_citation_db(read_only, use_duckdb)
```

Get connection to citation database.

## `get_html_db`

```python
def get_html_db(read_only, use_duckdb)
```

Get connection to HTML database.

## `get_embeddings_db`

```python
def get_embeddings_db(read_only, use_duckdb)
```

Get connection to embeddings database.

## `get_american_law_db`

```python
def get_american_law_db(read_only, use_duckdb)
```

Get connection to citation database.
