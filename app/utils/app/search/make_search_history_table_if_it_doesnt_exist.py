# """
# Utility for creating the search_history table for storing user search history.

# This module provides functionality to create the database table
# that stores user search history for later retrieval and display.
# """
# import duckdb


# from configs import configs
# from logger import logger


# class SearchHistoryTable:
#     """
#     Class for managing the search history table schema.
    
#     This class provides methods for creating and initializing
#     the search_history table and its associated indexes.
#     """
    
#     # SQL statements for table and index creation
#     CREATE_TABLE = '''
#     CREATE TABLE IF NOT EXISTS search_history (
#         search_history_cid VARCHAR PRIMARY KEY,
#         search_query_cid VARCHAR NOT NULL,
#         search_query TEXT NOT NULL,
#         client_id VARCHAR NOT NULL,
#         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         result_count INTEGER NOT NULL,
#     )
#     '''
    
#     CREATE_CLIENT_ID_INDEX = '''
#     CREATE INDEX IF NOT EXISTS idx_search_history_client_id 
#     ON search_history (client_id)
#     '''
    
#     CREATE_TIMESTAMP_INDEX = '''
#     CREATE INDEX IF NOT EXISTS idx_search_history_timestamp 
#     ON search_history (timestamp)
#     '''
    
#     @classmethod
#     def make_search_history_table_if_it_doesnt_exist(cls) -> None:
#         """
#         Creates the search_history table in the database if it doesn't already exist.
        
#         This method connects to the database and executes a CREATE TABLE IF NOT EXISTS
#         statement to ensure the search_history table is available for storing user search
#         history. The table stores search queries, timestamps, and associated search results.
        
#         The algorithm:
#         1. Connect to the database with write access
#         2. Create a cursor for executing SQL
#         3. Execute the CREATE TABLE IF NOT EXISTS statement with the required schema
#         4. Create indexes for efficient querying
        
#         Args:
#             None
            
#         Returns:
#             None
            
#         Example:
#             ```python
#             # Call at application startup to ensure the table exists
#             SearchHistoryTable.make_search_history_table_if_it_doesnt_exist()
            
#             # Now search_history table is ready to be used for storing search history
#             ```
            
#         Notes:
#             - search_history_cid is a CID of the search_query CID and timestamp
#             - search_query_cid is used to link to the cached query results 
#             - timestamp is automatically set to the current time when a record is inserted
#             - client_id enables storing history for different users/sessions
#         """
#         with duckdb.connect(configs.SEARCH_HISTORY_DB_PATH, read_only=False) as conn:
#             with conn.cursor() as cursor:
#                 # Create the table if it doesn't exist
#                 cursor.execute(cls.CREATE_TABLE)
                
#                 # Create an index on client_id for faster lookups
#                 cursor.execute(cls.CREATE_CLIENT_ID_INDEX)
                
#                 # Create an index on timestamp for faster sorting
#                 cursor.execute(cls.CREATE_TIMESTAMP_INDEX)
                
#                 logger.info("Created/verified search_history table")


# # Alias for backward compatibility
# make_search_history_table_if_it_doesnt_exist = SearchHistoryTable.make_search_history_table_if_it_doesnt_exist