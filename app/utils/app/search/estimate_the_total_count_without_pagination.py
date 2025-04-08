"""
Utility for estimating the total number of results from a SQL query.

This module provides a function to count the total number of results that
would be returned by a SQL query, useful for pagination calculations.
"""
from app import logger
from .type_vars import SqlCursor


def estimate_the_total_count_without_pagination(cursor: SqlCursor, sql_query: str) -> int:
    """
    Estimates the total count of records that would be returned by a SQL query.
    
    This function takes a SQL query and wraps it in a COUNT(*) query to determine
    the total number of records that would be returned without pagination. This is
    useful for calculating total pages and other pagination parameters.
    
    The algorithm:
    1. Construct a COUNT(*) query that wraps the original SQL query as a subquery
    2. Execute the COUNT(*) query on the given cursor
    3. Fetch the single result (total count)
    4. Log the total count for debugging purposes
    5. Return the total count as an integer
    
    Args:
        cursor: A database cursor that can execute SQL queries
        sql_query: The original SQL query whose results we want to count
        
    Returns:
        int: The total number of records that would be returned by the SQL query
        
    Example:
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
    """
    count_query = f"SELECT COUNT(*) AS total FROM ({sql_query}) as subquery"
    cursor.execute(count_query)
    total = cursor.fetchone()[0]
    logger.debug(f"Total results from SQL query: {total}")
    return total