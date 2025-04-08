# _get_data_from_sql.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/_get_data_from_sql.py`

## Module Description

Utility module for executing SQL queries and retrieving results in different formats.

This module provides functions to execute SQL queries on a DuckDB database
and format the results as dictionaries, tuples, or pandas DataFrames.

## Table of Contents

### Functions

- [`_validate_get_data_from_sql`](#_validate_get_data_from_sql)
- [`get_data_from_sql`](#get_data_from_sql)

## Functions

## `_validate_get_data_from_sql`

```python
def _validate_get_data_from_sql(sql_query, cursor, return_a)
```

Validates parameters for the get_data_from_sql function.

**Parameters:**

- `sql_query` (`Any`): The SQL query to validate
cursor: The database cursor to validate
return_a: The return format string to validate

**Raises:**

- `ValueError`: If sql_query is None or return_a is not one of 'dict', 'tuple', or 'df'
TypeError: If cursor is not a DuckDBPyConnection

## `get_data_from_sql`

```python
def get_data_from_sql(cursor, return_a, sql_query, how_many)
```

Executes a SQL query and returns the results in the specified format.

This function executes the provided SQL query on the given cursor and returns
the results in one of three formats: a list of dictionaries, a list of tuples,
or a pandas DataFrame. When returning tuples, you can specify how many results
to fetch.

**Parameters:**

- `cursor` (`duckdb.DuckDBPyConnection`): A DuckDB database cursor to execute the query on
return_a: The format to return results in ('dict', 'tuple', or 'df')
sql_query: The SQL query to execute or a tuple with the query and parameters
how_many: For 'tuple' format, how many results to fetch (None=all, 1=one result)

**Returns:**

- `list[dict[str, Any]] | list[tuple[str, Any]] | tuple | pd.DataFrame`: - 'dict': A list of dictionaries, each representing a row
    - 'tuple': A list of tuples or a single tuple, depending on how_many
    - 'df': A pandas DataFrame with the query results

**Raises:**

- `ValueError`: If sql_query is None, return_a is invalid, or how_many is invalid
TypeError: If cursor is not a DuckDBPyConnection

**Examples:**

```python
```python
    cursor = get_a_database_connection()
    
    # Get results as a list of dictionaries
    results_dict = get_data_from_sql(
        cursor=cursor,
        sql_query="SELECT * FROM citations LIMIT 5"
    )
    
    # Get results as a pandas DataFrame
    results_df = get_data_from_sql(
        cursor=cursor,
        return_a='df',
        sql_query="SELECT * FROM citations LIMIT 5"
    )
    
    # Get a single result as a tuple
    result_tuple = get_data_from_sql(
        cursor=cursor,
        return_a='tuple',
        sql_query="SELECT * FROM citations LIMIT 1",
        how_many=1
    )
    ```
```
