# test_database_migration.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/tests/test_database_migration.py`

## Table of Contents

### Functions

- [`setup_citation_db_sqlite`](#setup_citation_db_sqlite)
- [`setup_html_db_sqlite`](#setup_html_db_sqlite)
- [`setup_embeddings_db_sqlite`](#setup_embeddings_db_sqlite)
- [`setup_citation_db_duckdb`](#setup_citation_db_duckdb)
- [`setup_html_db_duckdb`](#setup_html_db_duckdb)
- [`setup_embeddings_db_duckdb`](#setup_embeddings_db_duckdb)

### Classes

- [`TestDatabaseMigration`](#testdatabasemigration)

## Functions

## `setup_citation_db_sqlite`

```python
def setup_citation_db_sqlite(db_path)
```

Setup citation database with SQLite.

## `setup_html_db_sqlite`

```python
def setup_html_db_sqlite(db_path)
```

Setup HTML database with SQLite.

## `setup_embeddings_db_sqlite`

```python
def setup_embeddings_db_sqlite(db_path)
```

Setup embeddings database with SQLite.

## `setup_citation_db_duckdb`

```python
def setup_citation_db_duckdb(db_path)
```

Setup citation database with DuckDB.

## `setup_html_db_duckdb`

```python
def setup_html_db_duckdb(db_path)
```

Setup HTML database with DuckDB.

## `setup_embeddings_db_duckdb`

```python
def setup_embeddings_db_duckdb(db_path)
```

Setup embeddings database with DuckDB.

## Classes

## `TestDatabaseMigration`

```python
class TestDatabaseMigration(object)
```

Tests for database migration from SQLite to DuckDB.

**Methods:**

- [`temp_db_dir`](#testdatabasemigrationtemp_db_dir)
- [`test_duckdb_citation_db_setup`](#testdatabasemigrationtest_duckdb_citation_db_setup)
- [`test_duckdb_embeddings_db_setup`](#testdatabasemigrationtest_duckdb_embeddings_db_setup)
- [`test_duckdb_html_db_setup`](#testdatabasemigrationtest_duckdb_html_db_setup)
- [`test_sqlite_citation_db_setup`](#testdatabasemigrationtest_sqlite_citation_db_setup)
- [`test_sqlite_embeddings_db_setup`](#testdatabasemigrationtest_sqlite_embeddings_db_setup)
- [`test_sqlite_html_db_setup`](#testdatabasemigrationtest_sqlite_html_db_setup)

### `temp_db_dir`

```python
def temp_db_dir(self, self)
```

Create a temporary directory for test databases.

### `test_duckdb_citation_db_setup`

```python
def test_duckdb_citation_db_setup(self, temp_db_dir)
```

Test creating and querying the DuckDB citation database.

### `test_duckdb_embeddings_db_setup`

```python
def test_duckdb_embeddings_db_setup(self, temp_db_dir)
```

Test creating and querying the DuckDB embeddings database.

### `test_duckdb_html_db_setup`

```python
def test_duckdb_html_db_setup(self, temp_db_dir)
```

Test creating and querying the DuckDB HTML database.

### `test_sqlite_citation_db_setup`

```python
def test_sqlite_citation_db_setup(self, temp_db_dir)
```

Test creating and querying the SQLite citation database.

### `test_sqlite_embeddings_db_setup`

```python
def test_sqlite_embeddings_db_setup(self, temp_db_dir)
```

Test creating and querying the SQLite embeddings database.

### `test_sqlite_html_db_setup`

```python
def test_sqlite_html_db_setup(self, temp_db_dir)
```

Test creating and querying the SQLite HTML database.
