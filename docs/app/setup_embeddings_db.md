# setup_embeddings_db.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/api/database/setup_embeddings_db.py`

## Table of Contents

### Functions

- [`setup_embeddings_db`](#setup_embeddings_db)
- [`_setup_embeddings_db_sqlite`](#_setup_embeddings_db_sqlite)
- [`_setup_embeddings_db_duckdb`](#_setup_embeddings_db_duckdb)

## Functions

## `setup_embeddings_db`

```python
def setup_embeddings_db(db_path, use_duckdb)
```

Set up the embeddings database schema.

**Parameters:**

- `db_path` (`Any`): Optional path to database file, defaults to embeddings_db_path
use_duckdb: Whether to use DuckDB (True) or SQLite (False)

**Returns:**

- `Union[(sqlite3.Connection, duckdb.DuckDBPyConnection)]`: Database connection object

## `_setup_embeddings_db_sqlite`

```python
def _setup_embeddings_db_sqlite(db_path)
```

Setup embeddings database with SQLite.

## `_setup_embeddings_db_duckdb`

```python
def _setup_embeddings_db_duckdb(db_path)
```

Setup embeddings database with DuckDB.
