# create_american_law_db.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/api/database/create_american_law_db.py`

## Table of Contents

### Functions

- [`make_the_html_citations_and_embeddings_databases`](#make_the_html_citations_and_embeddings_databases)
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
- [`download_parquet_files_from_hugging_face`](#download_parquet_files_from_hugging_face)
- [`create_american_law_db`](#create_american_law_db)

## Functions

## `make_the_html_citations_and_embeddings_databases`

```python
def make_the_html_citations_and_embeddings_databases()
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

Insert citation data from parquet files into the citation database.

This function reads citation data from parquet files and inserts it into
the citations database. It handles transaction management and logs errors.

**Parameters:**

- `parquets (list[tuple[str, Path]])` (`Any`): A list of tuples containing the table name
and path to the parquet file. Each tuple should have format (table_name, file_path).

**Returns:**

- `None`: None

## `log_missing_data`

```python
def log_missing_data(gnis, missing_data, csv_path)
```

Log missing parquet files for a given GNIS to a CSV file.

## `attach_then_insert_from_another_db`

```python
def attach_then_insert_from_another_db(merged_db, db_path)
```

Attach another database and insert its data into the merged database.

This function attaches a database at the specified path to the current connection,
transfers all data from the table with the same name as the database stem,
and then detaches the database. The operation is wrapped in a transaction
for atomicity.

**Parameters:**

- `merged_db (duckdb.DuckDBPyConnection)` (`Any`): The connection to the database that will
receive the data.
db_path (Path): Path to the database to attach and copy data from.

**Returns:**

- `None`: None

## `insert_into_db_from_parquet_file`

```python
def insert_into_db_from_parquet_file(parquets)
```

Insert data from parquet files into their corresponding database tables.

This function processes a list of parquet files, connecting to the appropriate
database based on the first element in the list (which determines the database type),
then loads each parquet file into its corresponding table.

**Parameters:**

- `parquets (list[tuple[str, Path]])` (`Any`): A list of tuples containing the table name
and path to the parquet file. Each tuple should have format (table_name, file_path).
All entries should be for the same database type (citations, embeddings, or html).

**Returns:**

- `None`: None

## `get_all_the_unique_gnis_that_are_in_all_three_tables_in_the_database`

```python
def get_all_the_unique_gnis_that_are_in_all_three_tables_in_the_database(cursor)
```

Retrieve all unique GNIS identifiers that exist in all three database tables.

This function executes a SQL query that finds GNIS identifiers that have matching
content (via CID) across the embeddings, html, and citations tables. This identifies
locations with complete data across all three tables.

**Parameters:**

- `cursor (duckdb.DuckDBPyConnection)` (`Any`): A cursor to the DuckDB database connection
that contains the three tables (embeddings, html, and citations).

**Returns:**

- `set[str]`: A set of unique GNIS identifiers present in all three tables

## `check_for_complete_set_of_parquet_files`

```python
def check_for_complete_set_of_parquet_files(unique_gnis, base_path)
```

Check for complete sets of parquet files (citation, html, and embedding) for each GNIS.

This function finds all citation parquet files and then checks if corresponding HTML
and embedding parquet files exist for each GNIS. It only includes a GNIS in the result
if all three file types exist and the citation file is readable.

**Parameters:**

- `unique_gnis (set[str])` (`Any`): Set of GNIS identifiers to exclude (already in the database)
base_path (Path): Base directory path for parquet files

**Returns:**

- `list[list[tuple[(str, Path)]]]`: A list of lists containing tuples of (table_name, file_path),
        organized by file type [citations_list, html_list, embeddings_list]

## `upload_files_to_database`

```python
def upload_files_to_database(parquet_list)
```

Upload parquet files to their corresponding databases using parallel processing.

This function uses process pooling to upload multiple parquet files in parallel.
It processes the list of lists of parquet files, sending each list to a separate
process for insertion into the appropriate database.

**Parameters:**

- `parquet_list (list[list[tuple[str, Path]]])` (`Any`): A list of lists containing tuples of
(table_name, file_path) organized by file type. Each sublist represents one
type of data (citations, html, or embeddings).

**Returns:**

- `None`: None

## `merge_database_into_the_american_law_db`

```python
def merge_database_into_the_american_law_db(cursor)
```

Merge individual databases (citations, embeddings, html) into the main american_law.db.

This function iterates through all defined databases in DB_DICT, attaches each one
to the american_law.db connection, and copies their data in chunks to manage memory usage.
It handles large datasets by splitting them into manageable chunks and includes retry
logic for failed chunks.

**Parameters:**

- `cursor (duckdb.DuckDBPyConnection)` (`Any`): Cursor to the american_law.db database connection

**Returns:**

- `None`: None

## `download_parquet_files_from_hugging_face`

```python
def download_parquet_files_from_hugging_face()
```

Download parquet files from Hugging Face.

## `create_american_law_db`

```python
def create_american_law_db()
```

Process the dataset and store in DuckDB database
