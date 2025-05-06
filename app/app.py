#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
The FastAPI application that serves as an API for accessing American law documents.
"""
from __future__ import annotations
from dotenv import load_dotenv
import json
from pathlib import Path
import sys
import traceback
from typing import Union


from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn


from .logger import logger


import app.paths.search as search
import app.paths.search_history as search_history
from app.schemas.law_item import LawItem
from app.schemas.error_response import ErrorResponse

from app.utils.database.get_db import get_html_db


# Load environment variables
load_dotenv()


# Set up the FastAPI app
app = FastAPI(title="American Law API", description="API for accessing American law database")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
frontend_path = Path(__file__).parent / 'frontend'
static_file_path = frontend_path / 'static'
templates_path = frontend_path / 'templates'

# Mount static files and templates
app.mount("/src", StaticFiles(directory=static_file_path), name="src")
templates = Jinja2Templates(directory=templates_path)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Serve the main index page of the application.
    
    This endpoint renders the main HTML template for the application,
    which is the entry point for the user interface.
    
    Args:
        request: The incoming request object
        
    Returns:
        HTMLResponse: The rendered index.html template
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Serve favicon
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """
    Serve the site favicon.
    
    This endpoint serves the favicon.ico file from the static images directory.
    It is marked as not included in the schema documentation.
    
    Returns:
        FileResponse: The favicon.ico file
    """
    favicon_path = static_file_path / 'images' / 'favicon' / 'favicon.ico'
    return FileResponse(favicon_path)

# Serve public assets directly:
@app.get("/public/{filename:path}")
async def serve_public_files(filename: str):
    """
    Serve static files from the public templates directory.
    
    This endpoint allows direct access to files in the templates directory
    via the /public/ URL path.
    
    Args:
        filename: The path of the file to serve
        
    Returns:
        FileResponse: The requested file
    """
    public_files_path = templates_path / filename
    return FileResponse(public_files_path)


@app.get("/side-menu/{filename:path}", response_class=HTMLResponse)
async def serve_side_menu_files(filename: str):
    """
    Serve HTML files from the side-menu templates directory.
    
    This endpoint serves HTML files from the side-menu subdirectory,
    such as about.html, contact.html, etc.
    
    Args:
        filename: The name of the file to serve from the side-menu directory
        
    Returns:
        HTMLResponse: The requested HTML file
    """
    side_menu_path = templates_path / 'side-menu' / filename
    return FileResponse(side_menu_path)


@app.get("/api/search/sse")
async def search_sse_response(
    q: str = Query("", description="Search query"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
    client_id: str = Depends(search_history.get_or_create_client_id),
):
    """
    Server-Sent Events endpoint that streams search results incrementally.
    
    This endpoint implements Server-Sent Events (SSE) to provide a streaming
    interface for search results. It allows the client to receive results
    incrementally as they become available, providing a more responsive user
    experience for searches that may take time to complete.
    
    The event stream includes:
    - A "search_started" event when the search begins
    - Multiple "results_update" events as results are found
    - A "search_complete" event when the search is finished
    - An "error" event if any errors occur during the search
    
    This endpoint also saves search queries to the user's search history.
    
    Args:
        q: The search query string
        page: The page number to retrieve
        per_page: The number of results per page
        client_id: Client identifier for search history tracking
        
    Returns:
        EventSourceResponse: A streaming response that sends events to the client
        
    Example:
        ```javascript
        // Client-side JavaScript
        const eventSource = new EventSource('/api/search/sse?q=zoning laws');
        eventSource.addEventListener('results_update', (event) => {
          const results = JSON.parse(event.data);
          // Update UI with results
        });
        ```
    """
    async def _event_generator():
        try:
            # Initial event to indicate the search has started
            yield {
                "event": "search_started",
                "data": json.dumps({
                    "message": "Search started",
                    "query": q
                })
            }

            # Include client_id for search history tracking
            async for result in search.function(q=q, page=page, per_page=per_page, client_id=client_id):
                # Send each result chunk as it becomes available
                yield {
                    "event": "results_update",
                    "data": json.dumps(result)
                }

            # Final event to indicate the search is complete
            yield {
                "event": "search_complete",
                "data": json.dumps({
                    "message": "Search completed",
                    "query": q
                })
            }

        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            traceback.print_exc()
            # Send error event
            yield {
                "event": "error",
                "data": json.dumps({
                    "message": str(e)
                })
            }
    
    return EventSourceResponse(_event_generator())

@app.get("/api/talk_with_the_law")


# Search history endpoints
@app.get("/api/search-history", response_model=search_history.SearchHistoryResponse)
async def get_search_history(
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(10, description="Items per page", ge=1, le=50),
    client_id: str = Depends(search_history.get_or_create_client_id)
):
    """
    Get the search history for the current user.
    
    This endpoint retrieves a paginated list of the user's previous searches.
    The user is identified by a client ID stored in cookies.
    
    Args:
        page: The page number to retrieve (1-based)
        per_page: The number of entries per page
        client_id: The client identifier from cookies
        
    Returns:
        SearchHistoryResponse: Paginated search history entries
        
    Example:
        ```
        GET /api/search-history?page=1&per_page=10
        ```
    """
    return await search_history.get_history(page, per_page, client_id)


@app.delete("/api/search-history/{search_id}", response_model=search_history.DeleteHistoryResponse)
async def delete_search_history_entry(
    search_id: int,
    client_id: str = Depends(search_history.get_or_create_client_id)
):
    """
    Delete a specific search history entry.
    
    This endpoint removes a single entry from the user's search history.
    The user is identified by a client ID stored in cookies.
    
    Args:
        search_id: The ID of the search history entry to delete
        client_id: The client identifier from cookies
        
    Returns:
        DeleteHistoryResponse: Result of the deletion operation
        
    Example:
        ```
        DELETE /api/search-history/42
        ```
    """
    return await search_history.delete_history_entry(search_id, client_id)


@app.delete("/api/search-history", response_model=search_history.DeleteHistoryResponse)
async def clear_search_history(
    client_id: str = Depends(search_history.get_or_create_client_id)
):
    """
    Clear all search history for the current user.
    
    This endpoint removes all entries from the user's search history.
    The user is identified by a client ID stored in cookies.
    
    Args:
        client_id: The client identifier from cookies
        
    Returns:
        DeleteHistoryResponse: Result of the clearing operation
        
    Example:
        ```
        DELETE /api/search-history
        ```
    """
    return await search_history.clear_history(client_id)


@app.get("/api/law/{cid}", response_model=Union[LawItem, ErrorResponse])
async def get_law(cid: str) -> dict:
    """
    API endpoint to retrieve a specific legal document by its content ID.
    
    This endpoint retrieves a single legal document by its unique content ID (CID).
    It returns the complete document including metadata and HTML content.
    
    The algorithm:
    1. Connect to the HTML database in read-only mode
    2. Execute a SQL query joining the citations and HTML tables
    3. Filter by the provided CID
    4. Format the result as a LawItem response
    5. Close database resources
    6. Return the document or a 404 error if not found
    
    Args:
        cid: The content identifier of the legal document to retrieve
        
    Returns:
        LawItem: The legal document with metadata and HTML content
        
    Raises:
        HTTPException: 404 error if the document is not found
        
    Example:
        ```
        GET /api/law/bafkreihvwc5kg3estvqpicmmqghwiriti6mz5w3lk4k3app3guwk6onrq4
        ```
    """
    html_conn = get_html_db(read_only=True)
    html_cursor = html_conn.cursor()
    try:
        html_cursor.execute('''
        SELECT *
        FROM citations c
        JOIN html h ON c.cid = h.cid
        WHERE c.cid = ?
        ''', (cid,))
        
        law: dict = html_cursor.fetchdf().to_dict('records')[0]
    finally:
        html_cursor.close()
        html_conn.close()
    logger.debug(f"law: {law}")
    
    if law:
        return {
            'cid': law['cid'],
            'title': law['title'],
            'chapter': law['chapter'],
            'place_name': law['place_name'],
            'state_name': law['state_name'],
            'date': law['date'],
            'bluebook_citation': law['bluebook_citation'],
            'html': law['html']
        }
    else:
        raise HTTPException(status_code=404, detail="Law not found")


if __name__ == '__main__':
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
    finally:
        logger.info("Server stopped.")
        sys.exit(0)