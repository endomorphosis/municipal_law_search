"""
Utility module for creating database connections to the American law database.

This module provides a simple interface for obtaining a database cursor,
with appropriate error handling for use in FastAPI routes.
"""
from fastapi import HTTPException


from app import logger
from app.utils.database.get_db import get_american_law_db
from app.utils.app.search.type_vars import SqlCursor


def get_a_database_connection() -> SqlCursor:
    """
    Creates and returns a database cursor for the American law database.
    
    This function attempts to create a connection to the American law database
    and returns a cursor for executing SQL queries. If the connection fails,
    it logs the error and raises an HTTPException with a 500 status code.
    
    The algorithm:
    1. Attempt to get a database connection using get_american_law_db()
    2. If connection fails (returns None), log the error and raise an HTTPException
    3. Otherwise, return a cursor for the database connection
    
    Args:
        None
        
    Returns:
        SqlCursor: A database cursor object for executing SQL queries
        
    Raises:
        HTTPException: If the database connection could not be established
            with status_code=500 and detail="Database connection failed"
    
    Example:
        ```python
        try:
            cursor = get_a_database_connection()
            cursor.execute("SELECT * FROM citations LIMIT 10")
            results = cursor.fetchall()
        except HTTPException as e:
            # Handle connection error
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        ```
    """
    db_conn = get_american_law_db()
    if db_conn is None:
        logger.error("Failed to get a database connection")
        raise HTTPException(status_code=500, detail="Database connection failed")
    return db_conn.cursor()