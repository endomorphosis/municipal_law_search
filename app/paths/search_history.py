# # -*- coding: utf-8 -*-
# """
# API endpoints for managing search history
# """
# from __future__ import annotations

# import traceback
# from typing import List, Optional

# from fastapi import Cookie, Depends, HTTPException, Query
# from pydantic import BaseModel
# import uuid

# from logger import logger

# from utils.app.search.make_search_history_table_if_it_doesnt_exist import (
#     SearchHistoryTable,
#     make_search_history_table_if_it_doesnt_exist
# )
# from utils.app.search.save_search_history import (
#     SearchHistory,
#     get_search_history, 
#     get_total_search_history_count, 
#     delete_search_history_entry,
#     clear_search_history
# )


# # Ensure the search_history table exists
# make_search_history_table_if_it_doesnt_exist()


# # Pydantic models for request/response validation
# class SearchHistoryEntry(BaseModel):
#     """
#     Model representing a single search history entry.
    
#     Attributes:
#         search_id: Unique identifier for the search entry
#         search_query: The text of the search query
#         search_query_cid: Content ID of the search query
#         timestamp: When the search was performed
#         result_count: Number of results returned by the search
#     """
#     search_id: int
#     search_query: str
#     search_query_cid: str
#     timestamp: str
#     result_count: int


# class SearchHistoryResponse(BaseModel):
#     """
#     Model representing the response for search history requests.
    
#     Attributes:
#         entries: List of search history entries
#         total: Total number of search history entries
#         page: Current page number
#         per_page: Number of entries per page
#         total_pages: Total number of pages
#     """
#     entries: List[SearchHistoryEntry]
#     total: int
#     page: int
#     per_page: int
#     total_pages: int


# class DeleteHistoryResponse(BaseModel):
#     """
#     Model representing the response for history deletion requests.
    
#     Attributes:
#         success: Whether the deletion was successful
#         message: A message describing the result
#     """
#     success: bool
#     message: str


# def get_or_create_client_id(client_id: Optional[str] = Cookie(None)) -> str:
#     """
#     Gets the client ID from cookies or creates a new one.
    
#     This function is used as a FastAPI dependency to ensure each request
#     has a valid client ID, either from an existing cookie or by generating
#     a new one.
    
#     Args:
#         client_id: The client ID from cookies, if available
        
#     Returns:
#         str: The client ID (existing or newly generated)
#     """
#     if not client_id:
#         # Generate a new client ID if none exists
#         client_id = str(uuid.uuid4())
#     return client_id


# async def get_history(
#     page: int = Query(1, description="Page number", ge=1),
#     per_page: int = Query(10, description="Items per page", ge=1, le=50),
#     client_id: str = Depends(get_or_create_client_id)
# ) -> SearchHistoryResponse:
#     """
#     API endpoint to retrieve a user's search history.
    
#     This endpoint returns a paginated list of the user's previous searches,
#     identified by their client ID (from cookies). It includes metadata such as
#     the timestamp and result count for each search.
    
#     Args:
#         page: The page number to retrieve (1-based)
#         per_page: The number of entries per page
#         client_id: The client identifier from cookies
        
#     Returns:
#         SearchHistoryResponse: The search history entries with pagination info
        
#     Raises:
#         HTTPException: If an error occurs while retrieving the history
#     """
#     try:
#         # Calculate offset for pagination
#         offset = (page - 1) * per_page
        
#         # Get search history entries
#         entries = get_search_history(client_id, limit=per_page, offset=offset)
        
#         # Get total count for pagination
#         total = get_total_search_history_count(client_id)
        
#         # Calculate total pages
#         total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        
#         # Create the response
#         response = SearchHistoryResponse(
#             entries=entries,
#             total=total,
#             page=page,
#             per_page=per_page,
#             total_pages=total_pages
#         )
        
#         return response
    
#     except Exception as e:
#         logger.error(f"Error retrieving search history: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# async def delete_history_entry(
#     search_id: int,
#     client_id: str = Depends(get_or_create_client_id)
# ) -> DeleteHistoryResponse:
#     """
#     API endpoint to delete a specific search history entry.
    
#     This endpoint allows users to delete a single search from their history.
#     The client ID is used to ensure users can only delete their own history.
    
#     Args:
#         search_id: The ID of the search history entry to delete
#         client_id: The client identifier from cookies
        
#     Returns:
#         DeleteHistoryResponse: The result of the deletion operation
        
#     Raises:
#         HTTPException: If the entry doesn't exist or an error occurs
#     """
#     try:
#         success = delete_search_history_entry(search_id, client_id)
        
#         if not success:
#             raise HTTPException(
#                 status_code=404, 
#                 detail=f"Search history entry {search_id} not found or not owned by this client"
#             )
        
#         return DeleteHistoryResponse(
#             success=True,
#             message=f"Successfully deleted search history entry {search_id}"
#         )
    
#     except HTTPException:
#         raise
        
#     except Exception as e:
#         logger.error(f"Error deleting search history entry: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# async def clear_history(
#     client_id: str = Depends(get_or_create_client_id)
# ) -> DeleteHistoryResponse:
#     """
#     API endpoint to clear all search history for a user.
    
#     This endpoint allows users to delete their entire search history.
#     The client ID is used to ensure users can only delete their own history.
    
#     Args:
#         client_id: The client identifier from cookies
        
#     Returns:
#         DeleteHistoryResponse: The result of the clearing operation
        
#     Raises:
#         HTTPException: If an error occurs during clearing
#     """
#     try:
#         success = clear_search_history(client_id)
        
#         if not success:
#             raise HTTPException(
#                 status_code=500, 
#                 detail="Failed to clear search history"
#             )
        
#         return DeleteHistoryResponse(
#             success=True,
#             message="Successfully cleared all search history"
#         )
    
#     except HTTPException:
#         raise
        
#     except Exception as e:
#         logger.error(f"Error clearing search history: {e}")
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))