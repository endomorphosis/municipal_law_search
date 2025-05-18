from typing import Any
from unittest.mock import MagicMock
resources = {
    #"ranking_algorithm": MagicMock(),
    "text_search": MagicMock(),
    "image_search": MagicMock(),
    "voice_search": MagicMock(),
    "exact_match": MagicMock(),
    "fuzzy_match": MagicMock(),
    "string_exclusion": MagicMock(),
    #"filter_criteria": MagicMock(),
    #"multi_field_search": MagicMock(),
    #"query_parser": MagicMock(),
    #"db": MagicMock(),
}
from logger import logger
from elasticsearch import Elasticsearch, NotFoundError, RequestError, ConnectionError, TransportError
from elastic_transport import ObjectApiResponse


class ElasticsearchClient:

    def __init__(self, hosts=None):
        self.client = Elasticsearch(hosts=hosts or ["http://localhost:9200"])

    def query_parser(self, query: str, *args, **kwargs) -> str:
        """
        Parse and normalize a search query for Elasticsearch.
        
        Args:
            query (str): The raw search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            str: The parsed and normalized query.
        """
        # Handle empty queries
        if not query or not query.strip():
            return ""
            
        # Basic cleaning
        processed_query = query.strip()
        
        # Handle special Elasticsearch characters
        # Escape special characters: + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /
        special_chars = ['+', '-', '=', '&&', '||', '>', '<', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':', '\\', '/']
        
        # Don't escape characters that are part of Elasticsearch syntax
        # Check if it's a special query before escaping
        if any(op in processed_query for op in ["image:", "voice:", "\""]) or processed_query.startswith("-"):
            # Keep special query operators intact
            pass
        else:
            # Escape special characters for regular text searches
            for char in special_chars:
                if char in processed_query:
                    processed_query = processed_query.replace(char, f"\\{char}")

        # Apply any custom transformations from kwargs
        if kwargs.get('lowercase', True):
            processed_query = processed_query.lower()
            
        return processed_query


    def ranking_algorithm(self, query: str, results: list[str], *args, **kwargs):
        """
        Rank search results based on relevance to the query.
        
        Args:
            query (str): The search query
            results (list): The search results to rank
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            list: Ranked search results
        """
        # Let Elasticsearch handle the ranking using its built-in relevance scoring
        if not results:
            return []

        # Extract the query terms for possible boosting
        query_terms = query.lower().split()
        
        # Process the results from Elasticsearch
        processed_results = []
        for hit in results:
            if isinstance(hit, dict) and '_source' in hit:
                # Elasticsearch results typically have '_source' containing the document
                # and '_score' containing the relevance score
                score = hit.get('_score', 0)
                
                # Apply additional boosting if needed based on the query
                if kwargs.get('boost_fields'):
                    for field, boost in kwargs.get('boost_fields').items():
                        if field in hit.get('_source', {}) and any(term in str(hit['_source'][field]).lower() for term in query_terms):
                            score *= boost
                            hit['_score'] = score
                            
                processed_results.append(hit)
        
        # Sort results by _score field if available
        if isinstance(results, list) and all(isinstance(r, dict) for r in results):
            ranked_results = sorted(results, key=lambda x: x.get('_score', 0), reverse=True)
        else:
            # Sort by score in descending order
            ranked_results = sorted(processed_results, key=lambda x: x.get('_score', 0), reverse=True)

        # Apply any custom ranking logic here
        # For example, you could boost results based on certain fields
        # or apply domain-specific ranking rules
        # TODO: Implement custom ranking logic if needed

        return ranked_results

    def multi_field_search(self, processed_query: str, weighted_fields: list[str], *args, **kwargs) -> list[dict[str, Any]]:
        """
        Search across multiple fields with configurable weights.

        Args:
            processed_query (str): The search query.
            weighted_fields (list[str]): The fields to search in.
            weights (list[float], optional): The weights for each field. Defaults to None.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results.
        """
        # Construct the Elasticsearch query
        search_body = {
            "query": {
                "multi_match": {
                    "query": processed_query,
                    "fields": weighted_fields,
                    "type": kwargs.get("match_type", "best_fields"),
                    "operator": kwargs.get("operator", "or"),
                    "fuzziness": kwargs.get("fuzziness", "AUTO")
                }
            },
            "size": kwargs.get("size", 10)
        }
        
        # Add any additional filters
        if "filters" in kwargs:
            search_body["post_filter"] = kwargs["filters"]
            
        # Execute search against the specified index
        index = kwargs.get("index", "_all")
        try:
            response: ObjectApiResponse = self.client.search(index=index, body=search_body)
            results = response.get("hits", {}).get("hits", [])
            
            # Apply ranking if needed
            if kwargs.get("apply_ranking", True):
                return self.ranking_algorithm(processed_query, results, *args, **kwargs)
            return results

        except Exception as e:
            # Log the error and return empty results
            logger.exception(f"Error in multi_field_search: {e}")
            return []

    def filter_criteria(self, criteria: dict[str, Any], *args, **kwargs) -> list[dict[str, Any]]:
        """
        Apply arbitrary filtering criteria to search results.
        
        Args:
            criteria (dict[str, Any]): Dictionary of field-value pairs to filter by.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: The filtered search results.
        """
        index = kwargs.get("index", "_all")
        query = kwargs.get("query", "")
        size = kwargs.get("size", 10)

        # Build the Elasticsearch query
        search_body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "size": size
        }
        
        # If a text query is provided, add it to the must clause
        if query:
            search_body["query"]["bool"]["must"].append({
                "match": {
                    "text": query
                }
            })
        
        # Add filter criteria
        for field, value in criteria.items():
            match value:
                case list():
                    # For lists, use terms query
                    search_body["query"]["bool"]["filter"].append({
                        "terms": {
                            field: value
                        }
                    })
                case dict() if ('gte' in value or 'lte' in value or 'gt' in value or 'lt' in value):
                    # For range queries
                    search_body["query"]["bool"]["filter"].append({
                        "range": {
                            field: value
                        }
                    })
                case _:
                    # For exact matches
                    search_body["query"]["bool"]["filter"].append({
                        "term": {
                            field: value
                        }
                    })
        
        try:
            response = self.client.search(index=index, body=search_body)
            results = response.get("hits", {}).get("hits", [])
            
            # Apply ranking if specified
            if kwargs.get("apply_ranking", False) and query:
                return self.ranking_algorithm(query, results, *args, **kwargs)
            
            return results
            
        except Exception as e:
            logger.exception(f"Error in filter_criteria: {e}")
            return []

    def text_search(self, query: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform a text-based search operation.
        
        Args:
            query (str): The text search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results.
        """
        index = kwargs.get("index", "_all")
        size = kwargs.get("size", 10)
        
        # Process the query
        processed_query = self.query_parser(query, *args, **kwargs)
        if not processed_query:
            return []
            
        # Define the fields to search in with optional weights
        fields = kwargs.get("fields", ["text^3", "title^2", "content", "description"])
        
        # Build the search body
        search_body = {
            "query": {
                "query_string": {
                    "query": processed_query,
                    "fields": fields,
                    "default_operator": kwargs.get("operator", "OR"),
                    "fuzziness": kwargs.get("fuzziness", "AUTO")
                }
            },
            "size": size
        }
        
        # Execute the search
        try:
            response = self.client.search(index=index, body=search_body)
            results = response.get("hits", {}).get("hits", [])
            
            # Apply ranking if needed
            if kwargs.get("apply_ranking", True):
                return self.ranking_algorithm(query, results, *args, **kwargs)
            return results
            
        except Exception as e:
            logger.exception(f"Error in text_search: {e}")
            return []



    def search(self, index, body):
        return self.client.search(index=index, body=body)

    def index(self, index, document):
        return self.client.index(index=index, document=document)

    def delete(self, index, id):
        return self.client.delete(index=index, id=id)