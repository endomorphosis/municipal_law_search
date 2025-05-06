"""
Utility for sorting search results by similarity score and saving them to cache.

This module provides functions for organizing search results by relevance
and caching them in the search_query table for future retrieval, which
improves performance for repeated searches.
"""
from typing import Literal


import duckdb
from pydantic import BaseModel, Field


from app import configs 
from app import logger


class _SearchQuery(BaseModel):
    """
    A Pydantic model representing a search query and its cached results.
    
    This model stores a search query, its embedding vector, and the content IDs
    of the top 100 most relevant results, enabling fast retrieval of previous
    search results.
    
    Attributes:
        search_query_cid: The content identifier for the search query
        search_query: The original search query text
        embedding: The vector embedding of the search query (OpenAI's small embedding, 1536 dimensions)
        total_results: The total number of results found for this query
        cids_for_top_100: A comma-separated string of content IDs for the top 100 results
    """
    search_query_cid: str
    search_query: str
    embedding: list = Field(max_length=1536, min_length=1536) # NOTE Length of OpenAI's small embedding.
    total_results: int
    cids_for_top_100: str

    def to_tuple(self):
        """
        Convert the Pydantic model to a tuple for database insertion.
        
        Returns:
            tuple: A tuple containing all model fields in order for SQL insertion
        """
        return (
            self.search_query_cid,
            self.search_query,
            self.embedding,
            self.total_results,
            self.cids_for_top_100,
        )


def sort_and_save_search_query_results(
    search_query_cid: str = None,
    search_query: str = None,
    search_query_embedding: list[float] = None,
    query_table_embedding_cids: list[tuple[str, float]] = None,
    total: int = None,
) -> None:
    """
    Sorts search results by similarity score and saves them to the search_query table.
    
    This function takes a list of content IDs with their similarity scores, sorts them
    by score, extracts the top 100 results, and saves them to the search_query table
    along with the original query information. This creates a cache of search results
    that can be reused for identical or similar future queries.
    
    The algorithm:
    1. Sort the query_table_embedding_cids by similarity score in descending order
    2. Extract the top 100 content IDs from the sorted results
    3. Create a _SearchQuery object with the query information and top results
    4. Connect to the database and insert or replace the record in the search_query table
    5. Log the result of the operation
    
    Args:
        search_query_cid: The content identifier for the search query
        search_query: The original search query text
        search_query_embedding: The vector embedding of the search query
        query_table_embedding_cids: A list of tuples containing (content_id, similarity_score)
        total: The total number of results found for this query
        
    Returns:
        None
        
    Example:
        ```python
        # After performing a search and calculating similarity scores
        sort_and_save_search_query_results(
            search_query_cid="bafkreihvwc5kg3estvqpicmmqghwiriti6mz5w3lk4k3app3guwk6onrq4",
            search_query="zoning laws in California",
            search_query_embedding=[0.1, 0.2, ...],  # 1536-dimensional vector
            query_table_embedding_cids=[
                ("bafkreiabc123", 0.92),
                ("bafkreidef456", 0.85),
                # ... more results with scores
            ],
            total=157
        )
        ```
    """
    # Sort the overall results by similarity score.
    query_table_embedding_cids = sorted(query_table_embedding_cids, key=lambda x: x[1], reverse=True)
    #logger.debug(f"query_table_embedding_cids: {query_table_embedding_cids}")

    # String them together in that order for the query.
    top_100_cids = [cid for cid, _ in query_table_embedding_cids[:100]]
    #logger.debug(f"top_100_cids: {top_100_cids}")

    # If search_query_embedding is a list of list of floats, flatten it.
    # TODO This is hacky, refactor this to be more robust.
    if len(search_query_embedding) == 1 and isinstance(search_query_embedding[0], list):
        search_query_embedding = search_query_embedding[0]

    # Save the results CIDs to the query_hash table
    logger.info("Saving top 100 query results to search_query table...")
    search_query_tuple = _SearchQuery(
        search_query_cid=search_query_cid,
        search_query=search_query,
        embedding=search_query_embedding,
        total_results=total,
        cids_for_top_100=','.join(top_100_cids)
    ).to_tuple()

    with duckdb.connect(configs.AMERICAN_LAW_DB_PATH, read_only=False) as conn:
        with conn.cursor() as cursor:
            try:
                conn.begin()
                cursor.execute('''
                INSERT OR REPLACE INTO search_query (
                    search_query_cid, 
                    search_query, 
                    embedding, 
                    total_results, 
                    cids_for_top_100 
                ) 
                VALUES (?, ?, ?, ?, ?)
                ''', search_query_tuple)
                conn.commit()
                logger.info("Saved top 100 query results to search_query table.")
            except Exception as e:
                logger.error(f"Error inserting into search_query table: {e}")
                conn.rollback()