from typing import Literal


import duckdb
from pydantic import BaseModel, Field


from configs import configs
from logger import logger


class _SearchQuery(BaseModel):
    """
    A Pydantic model representing a search query.
    """
    search_query_cid: str
    search_query: str
    embedding: list[float] = Field(max_length=1536, min_length=1536) # Length of OpenAI's small embedding.
    total_results: int
    cids_for_top_100: str

    def to_tuple(self):
        """
        Convert the Pydantic model to a tuple for database insertion.
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

    # Sort the overall results by similarity score.
    query_table_embedding_cids = sorted(query_table_embedding_cids, key=lambda x: x[1], reverse=True)
    #logger.debug(f"query_table_embedding_cids: {query_table_embedding_cids}")

    # String them together in that order for the query.
    top_100_cids = [cid for cid, _ in query_table_embedding_cids[:100]]
    logger.debug(f"top_100_cids: {top_100_cids}")

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