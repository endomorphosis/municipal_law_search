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

    def order_by_cosine_similarity_score(self) -> None:
        """
        Sorts the search results by cosine similarity score in descending order.

        Returns:
            list[dict[str, Any]]: Sorted list of search results.
        """
        _sorted_results = sorted(self.results, key=lambda x: x.get('cosine_similarity_score', 0), reverse=True)
        self.results = _sorted_results
