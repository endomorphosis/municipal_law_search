# setup_html_db.py: last updated 03:23 PM on May 06, 2025

**File Path:** `app/api/database/setup_html_db.py`

## Table of Contents

### Functions

- [`setup_html_db`](#setup_html_db)
- [`_setup_html_db_sqlite`](#_setup_html_db_sqlite)
- [`_setup_html_db_duckdb`](#_setup_html_db_duckdb)

## Functions

## `setup_html_db`

```python
def setup_html_db(db_path=None, use_duckdb=True)
```

Set up the HTML database schema.

**Parameters:**

- `db_path` (`Any`): Optional path to database file, defaults to html_db_path

- `use_duckdb` (`Any`): Whether to use DuckDB (True) or SQLite (False)

**Returns:**

- `Union[(sqlite3.Connection, duckdb.DuckDBPyConnection)]`: Database connection object

## `_setup_html_db_sqlite`

```python
def _setup_html_db_sqlite(db_path)
```

Setup HTML database with SQLite.

## `_setup_html_db_duckdb`

```python
def _setup_html_db_duckdb(db_path)
```

Setup HTML database with DuckDB.
