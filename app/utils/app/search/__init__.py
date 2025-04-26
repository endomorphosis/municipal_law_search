
"""
Utilities for the search functionality in app.py.

This package contains utilities specifically designed to support the search
endpoint in app.py, providing database connection management, result caching,
embedding retrieval, pagination, and other search-related functionality.
"""
from utils.app.close_database_cursor import close_database_cursor
from utils.app.search.close_database_connection import close_database_connection
from utils.app.search.estimate_the_total_count_without_pagination import estimate_the_total_count_without_pagination
from utils.app.search.format_initial_sql_return_from_search import format_initial_sql_return_from_search
from utils.app.search.get_cached_query_results import get_cached_query_results
from utils.app.search.get_database_cursor import get_database_cursor
from utils.app.search.get_embedding_cids_for_all_the_cids import get_embedding_cids_for_all_the_cids
from utils.app.search.llm_sql_output import LLMSqlOutput
from utils.app.search.sort_and_save_search_query_results import sort_and_save_search_query_results
from utils.app.search.turn_english_into_sql import turn_english_into_sql
from utils.app.search.type_vars import SqlConnection, SqlCursor
from utils.app._get_data_from_sql import get_data_from_sql

from utils.app.search.make_search_query_table_if_it_doesnt_exist import make_search_query_table_if_it_doesnt_exist

__all__ = [
    "close_database_connection",
    "close_database_cursor",
    "estimate_the_total_count_without_pagination",
    "format_initial_sql_return_from_search",
    "get_cached_query_results",
    "get_data_from_sql",
    "get_database_cursor",
    "get_embedding_cids_for_all_the_cids",
    "LLMSqlOutput",
    "sort_and_save_search_query_results",
    "SqlConnection",
    "SqlCursor",
    "turn_english_into_sql",
    "make_search_query_table_if_it_doesnt_exist",
]

