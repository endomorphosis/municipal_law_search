"""
Utility for creating the search_query table for caching search results.

This module provides functionality to create the database table
that stores search queries and their results for efficient retrieval.
"""
import duckdb


from app import configs, Configs, logger


def make_search_query_table_if_it_doesnt_exist() -> None:
    """
    Creates the search_query table in the database if it doesn't already exist.
    
    This function connects to the database and executes a CREATE TABLE IF NOT EXISTS
    statement to ensure the search_query table is available for caching search results.
    The table stores search queries, their embeddings, total result counts, and the
    top 100 content IDs for each query.
    
    The algorithm:
    1. Connect to the database with write access
    2. Create a cursor for executing SQL
    3. Execute the CREATE TABLE IF NOT EXISTS statement with the required schema
    
    Args:
        None
        
    Returns:
        None
        
    Example:
        ```python
        # Call at application startup to ensure the table exists
        make_search_query_table_if_it_doesnt_exist()
        
        # Now search_query table is ready to be used for caching results
        ```
        
    Notes:
        - search_query_cid is generated from the hash of the query string
        - cids_for_top_100 stores a comma-separated string of content IDs
        - embedding stores the 1536-dimensional vector from OpenAI's model
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:
            # NOTE cids_for_top_100 is a string of 100 comma-separate CIDs.
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_query (
                search_query_cid VARCHAR PRIMARY KEY,
                search_query TEXT NOT NULL,
                embedding DOUBLE[1536] NOT NULL,
                total_results INTEGER NOT NULL,
                cids_for_top_100 TEXT NOT NULL,
            )
            ''')
