
"""
Utility for creating the stats table for tracking search performance.

This module provides functionality to create a database table for
recording statistics about search operations, such as execution time.
"""
import duckdb
from configs import configs


def make_stats_table() -> None:
    """
    Creates the stats table in the database if it doesn't already exist.
    
    This function connects to the database and executes a CREATE TABLE IF NOT EXISTS
    statement to ensure the stats table is available for recording performance
    metrics of search operations. Each record includes a unique run identifier,
    the search query identifier, and the execution time.
    
    The algorithm:
    1. Connect to the database
    2. Create a cursor for executing SQL
    3. Execute the CREATE TABLE IF NOT EXISTS statement with the required schema
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        ```python
        # Call at application startup to ensure the table exists
        make_stats_table()
        
        # Now stats table is ready to be used for performance tracking
        ```
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                run_cid VARCHAR PRIMARY KEY,
                search_query_cid VARCHAR NOT NULL,
                run_time DOUBLE NOT NULL,
            )
            ''')

