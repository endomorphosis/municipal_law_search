# create_american_law_db.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/api/database/create_american_law_db.py`

## Table of Contents

### Functions

- [`make_the_databases`](#make_the_databases)
- [`make_tables_in_the_databases`](#make_tables_in_the_databases)
- [`make_citations_db`](#make_citations_db)
- [`make_tables_in_citations_db`](#make_tables_in_citations_db)
- [`remake_citations_from_american_law_db`](#remake_citations_from_american_law_db)
- [`insert_into_db_from_citation_parquet_file`](#insert_into_db_from_citation_parquet_file)
- [`log_missing_data`](#log_missing_data)
- [`attach_then_insert_from_another_db`](#attach_then_insert_from_another_db)
- [`insert_into_db_from_parquet_file`](#insert_into_db_from_parquet_file)
- [`get_all_the_unique_gnis_that_are_in_all_three_tables_in_the_database`](#get_all_the_unique_gnis_that_are_in_all_three_tables_in_the_database)
- [`check_for_complete_set_of_parquet_files`](#check_for_complete_set_of_parquet_files)
- [`upload_files_to_database`](#upload_files_to_database)
- [`merge_database_into_the_american_law_db`](#merge_database_into_the_american_law_db)
- [`create_american_law_db`](#create_american_law_db)

## Functions

## `make_the_databases`

```python
def make_the_databases()
```

Create DuckDB databases if they do not exist.

## `make_tables_in_the_databases`

```python
def make_tables_in_the_databases()
```

Create tables in the DuckDB databases.

## `make_citations_db`

```python
def make_citations_db()
```

Create the citations database.

## `make_tables_in_citations_db`

```python
def make_tables_in_citations_db()
```

Create tables in the citations database.

## `remake_citations_from_american_law_db`

```python
def remake_citations_from_american_law_db()
```

Clear the citations table in the American Law database.

## `insert_into_db_from_citation_parquet_file`

```python
def insert_into_db_from_citation_parquet_file(parquets)
```

## `log_missing_data`

```python
def log_missing_data(gnis, missing_data, csv_path)
```

Log missing parquet files for a given GNIS to a CSV file.

## `attach_then_insert_from_another_db`

```python
def attach_then_insert_from_another_db(merged_db, db_path)
```

## `insert_into_db_from_parquet_file`

```python
def insert_into_db_from_parquet_file(parquets)
```

## `get_all_the_unique_gnis_that_are_in_all_three_tables_in_the_database`

```python
def get_all_the_unique_gnis_that_are_in_all_three_tables_in_the_database(cursor)
```

## `check_for_complete_set_of_parquet_files`

```python
def check_for_complete_set_of_parquet_files(unique_gnis, base_path)
```

## `upload_files_to_database`

```python
def upload_files_to_database(parquet_list)
```

## `merge_database_into_the_american_law_db`

```python
def merge_database_into_the_american_law_db(cursor)
```

## `create_american_law_db`

```python
def create_american_law_db(base_path)
```

Process the dataset and store in DuckDB database
