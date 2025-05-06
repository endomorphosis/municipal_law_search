"""
Utility for saving search query history.

This module provides functionality to save search queries to the search_history table,
enabling users to view their search history.
"""
import duckdb
from typing import Optional


from app import configs, logger

from datetime import datetime
import duckdb
from duckdb.typing import TIMESTAMP

from app.utils.common.get_cid import get_cid

def _get_datetime_iso_format() -> str:
    return datetime.now().isoformat()


def save_search_history(
    search_query_cid: str,
    search_query: str,
    client_id: str,
    result_count: int
) -> None:
    """
    Saves a search query to the search_history table.
    
    This function records a user's search query in the search_history table,
    along with metadata such as the client ID, timestamp, and result count.
    It enables the application to display search history to users.
    
    The algorithm:
    1. Connect to the database with write access
    2. Create a cursor for executing SQL
    3. Insert the search query information into the search_history table
    4. Handle any exceptions that occur during the database operation
    
    Args:
        search_query_cid: The content identifier for the search query
        search_query: The original search query text
        client_id: The identifier for the client/user/session
        result_count: The number of results returned by the search
        
    Returns:
        None
        
    Example:
        ```python
        # After performing a search
        save_search_history(
            search_query_cid="bafkreihvwc5kg3estvqpicmmqghwiriti6mz5w3lk4k3app3guwk6onrq4",
            search_query="zoning laws in California",
            client_id="user123",
            result_count=42
        )
        ```
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:

            # Register the timestamp function with DuckDB
            conn.create_function("_get_datetime_iso_format", _get_datetime_iso_format, [], TIMESTAMP)
            timestamp = _get_datetime_iso_format()
            try:
                conn.begin()
                cursor.execute('''
                INSERT INTO search_history (
                    search_history_cid,
                    search_query_cid,
                    search_query,
                    client_id,
                    timestamp,
                    result_count
                )
                VALUES (?, ?, ?, ?)
                ''', (
                    get_cid(search_query_cid, timestamp),
                    search_query_cid, 
                    search_query, 
                    client_id, 
                    timestamp,
                    result_count)
                )
                conn.commit()
                logger.info(f"Saved search history for query: {search_query}")
            except Exception as e:
                logger.error(f"Error saving search history: {e}")
                conn.rollback()


def get_search_history(
    client_id: str,
    limit: int = 10,
    offset: int = 0
) -> list[dict]:
    """
    Retrieves search history for a specific client.
    
    This function fetches the search history for a given client ID,
    ordered by timestamp with the most recent searches first.
    It supports pagination with limit and offset parameters.
    
    The algorithm:
    1. Connect to the database in read-only mode
    2. Create a cursor for executing SQL
    3. Execute a SELECT query to retrieve search history for the specified client
    4. Format the results as a list of dictionaries
    5. Return the formatted results
    
    Args:
        client_id: The identifier for the client/user/session
        limit: Maximum number of results to return (default: 10)
        offset: Number of results to skip (for pagination, default: 0)
        
    Returns:
        list[dict]: A list of dictionaries containing search history entries
        
    Example:
        ```python
        # Get the 10 most recent searches for a client
        history = get_search_history("user123")
        
        # Get the next 10 searches (pagination)
        more_history = get_search_history("user123", offset=10)
        ```
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=True) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute('''
                SELECT 
                    search_id,
                    search_query_cid,
                    search_query,
                    timestamp,
                    result_count
                FROM search_history
                WHERE client_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                ''', (client_id, limit, offset))
                
                # Convert results to a list of dictionaries
                results = cursor.fetchdf().to_dict('records')
                return results
            except Exception as e:
                logger.error(f"Error retrieving search history: {e}")
                return []


def get_total_search_history_count(client_id: str) -> int:
    """
    Gets the total count of search history entries for a specific client.
    
    This function returns the total number of search history entries
    for a given client ID, which is useful for pagination calculations.
    
    The algorithm:
    1. Connect to the database in read-only mode
    2. Create a cursor for executing SQL
    3. Execute a COUNT query to get the total number of entries
    4. Return the count
    
    Args:
        client_id: The identifier for the client/user/session
        
    Returns:
        int: The total number of search history entries for the client
        
    Example:
        ```python
        # Get the total number of searches for a client
        total = get_total_search_history_count("user123")
        ```
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=True) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute('''
                SELECT COUNT(*) AS total
                FROM search_history
                WHERE client_id = ?
                ''', (client_id,))
                
                result = cursor.fetchone()
                return result[0] if result else 0
            except Exception as e:
                logger.error(f"Error retrieving search history count: {e}")
                return 0


def delete_search_history_entry(search_id: int, client_id: str) -> bool:
    """
    Deletes a specific search history entry for a client.
    
    This function removes a single search history entry identified by
    search_id, but only if it belongs to the specified client_id.
    This ensures users can only delete their own search history.
    
    The algorithm:
    1. Connect to the database with write access
    2. Create a cursor for executing SQL
    3. Execute a DELETE statement with both search_id and client_id conditions
    4. Return a boolean indicating success
    
    Args:
        search_id: The ID of the search history entry to delete
        client_id: The identifier for the client/user/session
        
    Returns:
        bool: True if the entry was deleted, False otherwise
        
    Example:
        ```python
        # Delete a specific search history entry
        success = delete_search_history_entry(42, "user123")
        ```
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:
            try:
                conn.begin()
                cursor.execute('''
                DELETE FROM search_history
                WHERE search_id = ? AND client_id = ?
                ''', (search_id, client_id))
                
                conn.commit()
                logger.info(f"Deleted search history entry {search_id} for client {client_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting search history entry: {e}")
                conn.rollback()
                return False


def clear_search_history(client_id: str) -> bool:
    """
    Clears all search history for a specific client.
    
    This function removes all search history entries for a given client ID.
    It provides users with the ability to clear their entire search history.
    
    The algorithm:
    1. Connect to the database with write access
    2. Create a cursor for executing SQL
    3. Execute a DELETE statement to remove all entries for the client
    4. Return a boolean indicating success
    
    Args:
        client_id: The identifier for the client/user/session
        
    Returns:
        bool: True if the history was cleared, False otherwise
        
    Example:
        ```python
        # Clear all search history for a client
        success = clear_search_history("user123")
        ```
    """
    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:
            try:
                conn.begin()
                cursor.execute('''
                DELETE FROM search_history
                WHERE client_id = ?
                ''', (client_id,))
                
                conn.commit()
                logger.info(f"Cleared all search history for client {client_id}")
                return True
            except Exception as e:
                logger.error(f"Error clearing search history: {e}")
                conn.rollback()
                return False