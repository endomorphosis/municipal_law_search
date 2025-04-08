# make_stats_table.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/database/make_stats_table.py`

## Module Description

Utility for creating the stats table for tracking search performance.

This module provides functionality to create a database table for
recording statistics about search operations, such as execution time.

## Table of Contents

### Functions

- [`make_stats_table`](#make_stats_table)

## Functions

## `make_stats_table`

```python
def make_stats_table()
```

Creates the stats table in the database if it doesn't already exist.

This function connects to the database and executes a CREATE TABLE IF NOT EXISTS
statement to ensure the stats table is available for recording performance
metrics of search operations. Each record includes a unique run identifier,
the search query identifier, and the execution time.

**Returns:**

- `None`: None

**Examples:**

```python
```python
    # Call at application startup to ensure the table exists
    make_stats_table()
    
    # Now stats table is ready to be used for performance tracking
    ```
```
