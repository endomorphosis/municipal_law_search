
"""
Utilities for the search functionality in app.py.

This package contains utilities specifically designed to support the search
endpoint in app.py, providing database connection management, result caching,
embedding retrieval, pagination, and other search-related functionality.
"""
from app.utils.app.search.close_database_connection import close_database_connection
from app.utils.app.search.get_embedding_cids_for_all_the_cids import get_embedding_cids_for_all_the_cids
from app.utils.app.search.type_vars import SqlConnection, SqlCursor 
from app.utils.app.search.llm_sql_output import LLMSqlOutput
from app.utils.app.search.get_database_cursor import get_database_cursor
from app.utils.app.search.estimate_the_total_count_without_pagination import estimate_the_total_count_without_pagination
from app.utils.app.search.get_cached_query_results import get_cached_query_results
from app.utils.app.search.get_database_cursor import get_database_cursor
from app.utils.app.close_database_cursor import close_database_cursor
from app.utils.app.search.sort_and_save_search_query_results import sort_and_save_search_query_results
from app.utils.app._get_data_from_sql import get_data_from_sql


__all__ = [
    "get_embedding_cids_for_all_the_cids",
    "close_database_connection",
    "SqlConnection",
    "SqlCursor",
    "LLMSqlOutput",
    "get_database_cursor",
    "estimate_the_total_count_without_pagination",
    "get_cached_query_results",
    "close_database_cursor",
    "sort_and_save_search_query_results",
    "get_data_from_sql"
]

