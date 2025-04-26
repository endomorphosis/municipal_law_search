#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
The FastAPI application that serves as an API for accessing American law documents.
"""
from __future__ import annotations
from datetime import datetime
from dotenv import load_dotenv
import functools
import json
import os
from pathlib import Path
import sqlite3
import sys
import traceback
from typing import Any, AsyncGenerator, Callable, Coroutine, Never, TypeVar, Union


import duckdb
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, PositiveInt
from sse_starlette.sse import EventSourceResponse
import uvicorn


from logger import logger


import app.paths.search as search
from api.llm.async_interface import AsyncLLMInterface
from schemas.search_response import SearchResponse
from schemas.law_item import LawItem
from schemas.error_response import ErrorResponse

from utils.database.get_db import get_html_db


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

# Mount static files and templates
app.mount("/src", StaticFiles(directory="frontend/static"), name="src")
templates = Jinja2Templates(directory="frontend/templates")

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
favicon_path = Path(__file__).parent / 'frontend' / 'static'/ 'images' / 'favicon' / 'favicon.ico'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    """
    Serve the site favicon.
    
    This endpoint serves the favicon.ico file from the static images directory.
    It is marked as not included in the schema documentation.
    
    Returns:
        FileResponse: The favicon.ico file
    """
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
    return FileResponse(f"frontend/templates/{filename}")


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
    return FileResponse(f"frontend/templates/side-menu/{filename}")


@app.get("/api/search/sse")
async def search_sse_response(
    q: str = Query("", description="Search query"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(20, description="Items per page"),
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
    
    Args:
        q: The search query string
        page: The page number to retrieve
        per_page: The number of results per page
        
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
            
            # Process search results
            async for result in search.function(q=q, page=page, per_page=per_page):
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
        # Close the database connection when the server is stopped
        logger.info("Server stopped.")
        sys.exit(0)