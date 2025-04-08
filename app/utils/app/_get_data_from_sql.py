"""
Utility module for executing SQL queries and retrieving results in different formats.

This module provides functions to execute SQL queries on a DuckDB database
and format the results as dictionaries, tuples, or pandas DataFrames.
"""
from typing import Any, Never


import duckdb
import pandas as pd
from pydantic import PositiveInt


def _validate_get_data_from_sql(sql_query: Any, cursor: Any, return_a: str) -> Never:
    """
    Validates parameters for the get_data_from_sql function.
    
    The algorithm:
    1. Check if sql_query is None or empty
    2. Verify cursor is a DuckDB connection
    3. Ensure return_a is one of the allowed values
    
    Args:
        sql_query: The SQL query to validate
        cursor: The database cursor to validate
        return_a: The return format string to validate
        
    Raises:
        ValueError: If sql_query is None or return_a is not one of 'dict', 'tuple', or 'df'
        TypeError: If cursor is not a DuckDBPyConnection
    """
    if not sql_query:
        raise ValueError("SQL query cannot be None.")
    if not isinstance(cursor, duckdb.DuckDBPyConnection):
        raise TypeError("Cursor must be a DuckDB connection.")
    if return_a not in ['dict', 'tuple', 'df']:
        raise ValueError("return_a must be one of 'dict', 'tuple', or 'df'.")


def get_data_from_sql(
        cursor: duckdb.DuckDBPyConnection, 
        return_a: str = 'dict', 
        sql_query: str | tuple[str, tuple[Any,...]] = None, 
        how_many: PositiveInt = None
    ) -> list[dict[str, Any]] | list[tuple[str, Any]] | tuple | pd.DataFrame:
    """
    Executes a SQL query and returns the results in the specified format.
    
    This function executes the provided SQL query on the given cursor and returns
    the results in one of three formats: a list of dictionaries, a list of tuples,
    or a pandas DataFrame. When returning tuples, you can specify how many results
    to fetch.
    
    The algorithm:
    1. Validate the input parameters using _validate_get_data_from_sql
    2. Execute the SQL query on the provided cursor
    3. Depending on the return_a parameter:
       a. If 'dict': Return results as a list of dictionaries
       b. If 'tuple': Return results as a list of tuples, with options for how many
       c. If 'df': Return results as a pandas DataFrame
    
    Args:
        cursor: A DuckDB database cursor to execute the query on
        return_a: The format to return results in ('dict', 'tuple', or 'df')
        sql_query: The SQL query to execute or a tuple with the query and parameters
        how_many: For 'tuple' format, how many results to fetch (None=all, 1=one result)
        
    Returns:
        Depending on return_a:
        - 'dict': A list of dictionaries, each representing a row
        - 'tuple': A list of tuples or a single tuple, depending on how_many
        - 'df': A pandas DataFrame with the query results
        
    Raises:
        ValueError: If sql_query is None, return_a is invalid, or how_many is invalid
        TypeError: If cursor is not a DuckDBPyConnection
        
    Example:
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
    """
    _validate_get_data_from_sql(sql_query, cursor, return_a)

    cursor.execute(sql_query)
    match return_a:
        case 'dict':
            return cursor.fetchdf().to_dict('records')
        case 'tuple':
            if how_many is None: # Return a list of tuples
                return cursor.fetchall()
            elif how_many > 0: # Return a list of tuples of X size
                return cursor.fetchmany(how_many)
            elif how_many == 1: # Return a single tuple
                return cursor.fetchone()
            else:
                raise ValueError("how_many must be a positive integer.")
        case 'df':
            return cursor.fetchdf()