# estimate_the_total_count_without_pagination.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/estimate_the_total_count_without_pagination.py`

## Module Description

Utility for estimating the total number of results from a SQL query.

This module provides a function to count the total number of results that
would be returned by a SQL query, useful for pagination calculations.

## Table of Contents

### Functions

- [`estimate_the_total_count_without_pagination`](#estimate_the_total_count_without_pagination)

## Functions

## `estimate_the_total_count_without_pagination`

```python
def estimate_the_total_count_without_pagination(cursor, sql_query)
```

Estimates the total count of records that would be returned by a SQL query.

This function takes a SQL query and wraps it in a COUNT(*) query to determine
the total number of records that would be returned without pagination. This is
useful for calculating total pages and other pagination parameters.

**Parameters:**

- `cursor` (`SqlCursor`): A database cursor that can execute SQL queries
sql_query: The original SQL query whose results we want to count

**Returns:**

- `int`: The total number of records that would be returned by the SQL query

**Examples:**

```python
```python
    cursor = get_database_cursor()
    try:
        sql_query = "SELECT * FROM citations WHERE title LIKE '%zoning%'"
        total_count = estimate_the_total_count_without_pagination(cursor, sql_query)
        # total_count can be used to calculate pagination:
        total_pages = (total_count + page_size - 1) // page_size
    finally:
        close_database_cursor(cursor)
    ```
```
