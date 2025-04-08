from typing import Any


from pydantic import BaseModel


# Pydantic models for request/response validation
class SearchResponse(BaseModel):
    """
    Attributes:
        results (List[Dict[str, Any]]): List of search results.
        total (int): Total number of results.
        page (int): Current page number.
        per_page (int): Number of items per page.
        total_pages (int): Total number of pages.
    """
    results: list[dict[str, Any]]
    total: int
    page: int
    per_page: int
    total_pages: int