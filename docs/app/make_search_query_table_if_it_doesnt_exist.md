# make_search_query_table_if_it_doesnt_exist.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/make_search_query_table_if_it_doesnt_exist.py`

## Module Description

Utility for creating the search_query table for caching search results.

This module provides functionality to create the database table
that stores search queries and their results for efficient retrieval.

## Table of Contents

### Functions

- [`make_search_query_table_if_it_doesnt_exist`](#make_search_query_table_if_it_doesnt_exist)

## Functions

## `make_search_query_table_if_it_doesnt_exist`

```python
def make_search_query_table_if_it_doesnt_exist()
```

Creates the search_query table in the database if it doesn't already exist.

This function connects to the database and executes a CREATE TABLE IF NOT EXISTS
statement to ensure the search_query table is available for caching search results.
The table stores search queries, their embeddings, total result counts, and the
top 100 content IDs for each query.

**Returns:**

- `None`: None

**Examples:**

```python
```python
    # Call at application startup to ensure the table exists
    make_search_query_table_if_it_doesnt_exist()
    
    # Now search_query table is ready to be used for caching results
    ```
```
