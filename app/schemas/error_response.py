"""
Error response schema for the American Law Search API.

This module defines the standardized structure for error responses
returned by the API endpoints when exceptions occur.
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Standard error response model for API error handling.
    
    This model is used to provide consistent error responses across all API endpoints.
    It follows the common pattern of providing a human-readable error message in the
    detail field.
    
    Attributes:
        detail: A string containing a human-readable error message explaining what went wrong.
    
    Example:
        ```python
        error = ErrorResponse(detail="Citation not found")
        return JSONResponse(
            status_code=404,
            content=error.dict()
        )
        ```
    """
    detail: str