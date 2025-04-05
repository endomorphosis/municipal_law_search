# setup_citation_db.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/api/database/setup_citation_db.py`

## Table of Contents

### Functions

- [`setup_citation_db`](#setup_citation_db)
- [`_setup_citation_db_sqlite`](#_setup_citation_db_sqlite)
- [`_setup_citation_db_duckdb`](#_setup_citation_db_duckdb)

## Functions

## `setup_citation_db`

```python
def setup_citation_db(db_path, use_duckdb)
```

Set up the citation database schema.

**Parameters:**

- `db_path` (`Any`): Optional path to database file, defaults to citation_db_path
use_duckdb: Whether to use DuckDB (True) or SQLite (False)

**Returns:**

- `sqlite3.Connection | duckdb.DuckDBPyConnection`: Database connection object

## `_setup_citation_db_sqlite`

```python
def _setup_citation_db_sqlite(db_path)
```

Setup citation database with SQLite.

## `_setup_citation_db_duckdb`

```python
def _setup_citation_db_duckdb(db_path)
```

Setup citation database with DuckDB.
