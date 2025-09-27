import logging
from typing import Any, Callable, Mapping, Optional
from types import ModuleType
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
    #"parse_query": MagicMock(),
    #"db": MagicMock(),
}
from logger import logger
import elasticsearch
from elasticsearch import Elasticsearch, NotFoundError, RequestError, ConnectionError, TransportError
from elastic_transport import ObjectApiResponse


SPECIAL_CHARS = ['+', '-', '=', '&&', '||', '>', '<', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':', '\\', '/']


def _all_same_type(lst: list[Any], type_) -> bool:
    """Helper function to check if all elements in a list are of the same type."""
    if not isinstance(lst, list):
        raise TypeError(f"Expected a list, got {type(lst).__name__}")
    if not lst:
        return True
    return all(isinstance(item, type_) for item in lst)

def type_name(obj: Any) -> str:
    """Helper function to get the type name of an object."""
    return type(obj).__name__

class ElasticsearchClient:

    def __init__(self, 
                 hosts: list[str] = ["http://localhost:9200"], 
                 special_chars: list[str] = SPECIAL_CHARS,
                 elasticsearch: ModuleType = elasticsearch,
                 logger: logging.Logger = logger,
                 custom_ranking_algorithms: list[Callable] = []
                ) -> None:

        self.elasticsearch: ModuleType = elasticsearch
        self.client: Elasticsearch = self.elasticsearch.Elasticsearch(hosts=hosts)
        self.logger: logging.Logger = logger
        self.special_chars: list[str] = special_chars
        self.custom_ranking_algorithms: list[Callable] = custom_ranking_algorithms

        self.kwarg_type_mappings = {
            "index": (str, "_all"),
            "size": (int, 10),
            "match_type": (str, "best_fields"),
            "operator": (str, "or"),
            "fuzziness": ((str, int),"AUTO"),
            "filters": (dict, {}),
            "rank_results": (bool, True),
            "fields": (list, ["text^3", "title^2", "content", "description"]),
            "boost_fields": (dict, {}),
        }

    def _type_check_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Helper method to type check kwargs based on expected types."""
        output_kwargs = {}
        for key, (expected_type, default) in self.kwarg_type_mappings.items():
            if key not in kwargs:
                output_kwargs[key] = default
            else:
                value = type(kwargs[key])
                if not isinstance(value, expected_type):
                    raise TypeError(f"Expected type for '{key}' to be {expected_type}, got {type_name(value)}")
                output_kwargs[key] = value
        kwargs.update(output_kwargs)
        return kwargs

    def _value_check_kwargs(kwargs: dict[str, Any]) -> None:
        """Helper method to validate values of certain kwargs."""
        for key, value in kwargs.items():
            match key:
                case "index":
                    if not value:
                        raise ValueError("Index name cannot be an empty string")
                case "size":
                    if value <= 0:
                        raise ValueError(f"Size must be a positive integer, got {value}")
                case "operator":
                    if value not in ["AND", "OR"]:
                        raise ValueError(f"Operator must be 'AND' or 'OR', got {value}")
                case "fuzziness":
                    if isinstance(value, str) and value != "AUTO":
                        raise ValueError(f"Fuzziness string must be 'AUTO' if it is a string, got {value}")
                case "fields":
                    for field in value:
                        if not isinstance(field, str):
                            raise ValueError(f"All fields must be strings, got {type_name(field)}")
                case _:
                    pass  # No specific value checks for other keys


    def parse_query(self, query: str, lowercase: bool = True) -> str:
        """
        Parse and normalize a search query for Elasticsearch.
        
        Args:
            query (str): The raw search query.
            lowercase (bool): Whether to convert the query to lowercase. Defaults to True.

        Returns:
            str: The parsed and normalized query.
        """
        assert isinstance(query, str), f"Query must be a string, got {type(query).__name__}"
        assert isinstance(lowercase, bool), f"lowercase must be a boolean, got {type(lowercase).__name__}"

        stripped_query = query.strip()

        if not stripped_query:
            return ""

        ops = ["image:", "voice:", "\""]
        if not any(op in stripped_query for op in ops) or not stripped_query.startswith("-"):
            # Escape special characters for regular text searches
            # + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /
            for char in self.special_chars:
                if char in stripped_query:
                    stripped_query = stripped_query.replace(char, f"\\{char}")

        return stripped_query.lower() if lowercase else stripped_query


    def ranking_algorithm(self, query: str, *, results: list[str] | list[dict], **kwargs) -> list[str] | list[dict]:
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
        kwargs = self._type_check_kwargs(kwargs)
        self._value_check_kwargs(kwargs)


        assert isinstance(query, str), f"Query must be a string, got {type(query).__name__}"
        assert isinstance(results, list), f"Results must be a list, got {type(results).__name__}"
        for item in results:
            assert isinstance(item, (str, dict)), f"Each result must be a string or dictionary, got {type(item).__name__}"

        # Let Elasticsearch handle the ranking using its built-in relevance scoring
        if not results:
            return []

        # Extract the query terms for possible boosting
        query_terms = query.lower().split()

        # Process the results from Elasticsearch
        processed_results = []
        all_dict = _all_same_type(results, dict)

        if not all_dict or not _all_same_type(results, str):
            raise TypeError("Mixed result types detected; all results must be dictionaries for ranking")

        for hit in results:
            match hit:
                case str():
                    continue  # Skip string results for ranking
                case dict():
                    pass # Continue onto the rest of this block if it's a dict
                case _:
                    raise TypeError(f"Each result must be a string or dictionary, got {type(hit).__name__}")

            assert "_source" in hit, f"Each result dictionary must contain a '_source' key\n{hit}"
            assert "_score" in hit, f"Each result dictionary must contain a '_score' key\n{hit}"
            # Elasticsearch results typically have '_source' containing the document
            # and '_score' containing the relevance score
            score = hit.get('_score', 0)
            source = hit.get('_source', {})
            assert isinstance(source, dict), f"_source must be a dictionary, got {type(source).__name__}"
            assert isinstance(score, (int, float)), f"Score must be a number, got {type(score).__name__}"
            assert score >= 0, f"Score must be non-negative, got {score}"

            # Apply additional boosting if needed based on the query
            boost_fields = kwargs.get('boost_fields', {})
            assert isinstance(boost_fields, dict), f"boost_fields must be a dictionary, got {type(boost_fields).__name__}"

            # Avoid changing the dictionary while iterating
            hit_copy = hit.copy()

            if boost_fields:
                for field, boost in boost_fields.items():
                    if field in source and any(term in str(hit['_source'][field]).lower() for term in query_terms):
                        score *= boost
                        hit_copy['_score'] = score

            processed_results.append(hit_copy)

        # Sort results by _score field if available
        if all(isinstance(r, dict) for r in results):
            ranked_results = sorted(results, key=lambda x: x.get('_score', 0), reverse=True)
        else:
            # Sort by score in descending order
            ranked_results = sorted(processed_results, key=lambda x: x.get('_score', 0), reverse=True)

        # Apply any custom ranking logic here
            # For example, you could boost results based on certain fields
            # or apply domain-specific ranking rules
        if self.custom_ranking_algorithms:
            self.logger.debug(f"Applying {len(self.custom_ranking_algorithms)} custom ranking algorithms")
            for idx, alg in enumerate(self.custom_ranking_algorithms, start=1):
                self.logger.debug(f"Applying custom ranking algorithm {idx}: {alg.__name__}")
                try:
                    ranked_results = alg(query, ranked_results, **kwargs)
                except Exception as e:
                    raise AssertionError(f"Error in custom ranking algorithm {alg.__name__}: {e}") from e
        
        self.logger.debug(f"Ranked {len(ranked_results)} results for query: '{query}'\nTop 100 Results: {ranked_results[:100]}")

        return ranked_results


    def _execute_search(self, query: str, search_body: dict[str, Any],  kwargs: dict[str, Any] = {}) -> list[dict[str, Any]]:
        """Helper method to execute the search and retrieve results."""
        assert isinstance(query, str), f"Query must be a string, got {type(query).__name__}"
        assert isinstance(search_body, dict), f"search_body must be a dictionary, got {type(search_body).__name__}"
        assert isinstance(kwargs, dict), f"kwargs must be a dictionary, got {type(kwargs).__name__}"

        index = kwargs.get("index", "_all")
        rank_results = kwargs.get("rank_results", True)
        assert isinstance(index, str), f"Index must be a string, got {type(index).__name__}"
        assert isinstance(rank_results, bool), f"rank_results must be a boolean, got {type(rank_results).__name__}"

        response: ObjectApiResponse = self.search(index=index, body=search_body)
        results = response.get("hits", {}).get("hits", [])
        return self.ranking_algorithm(query, results, **kwargs) if rank_results and query else results


    def multi_field_search(self, processed_query: str, *, weighted_fields: list[str], **kwargs) -> list[dict[str, Any]]:
        """
        Search across multiple fields with configurable weights.

        Args:
            processed_query (str): The search query.
            weighted_fields (list[str]): The fields to search in.
            weights (list[float], optional): The weights for each field. Defaults to None.
            **kwargs: Additional keyword arguments. Options are:
                - index (str): The Elasticsearch index to search in. Defaults to "_all".
                - size (int): The number of results to return. Defaults to 10.
                - match_type (str): The type of multi-match query. Defaults to "best_fields"
                - operator (str): The operator for the query. Defaults to "or".
                - fuzziness (str|int): The fuzziness level. Defaults to "AUTO".
                - filters (dict): Additional filters to apply.
                - rank_results (bool): Whether to apply ranking. Defaults to True.
            
        Returns:
            list[dict[str, Any]]: The search results.
        """
        try:
            kwargs = self._type_check_kwargs(kwargs)
            self._value_check_kwargs(kwargs)
        except (TypeError, ValueError) as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during kwargs validation: {e}") from e

        multi_match = {
            "query": processed_query,
            "fields": weighted_fields,
            "type": kwargs.get("match_type", "best_fields"),
            "operator": kwargs.get("operator", "or"),
            "fuzziness": kwargs.get("fuzziness", "AUTO")
        }

        # Construct the Elasticsearch query
        search_body = {
            "query": {"multi_match": multi_match},
            "size": kwargs.get("size", 10),
            "post_filter": kwargs.get("filters", {})
        }

        # Execute search against the specified index
        try:
            self._execute_search(processed_query, search_body, kwargs=kwargs)
        except Exception as e:
            raise RuntimeError(f"Unexpected error when executing elasticsearch search: {e}") from e

    def filter_criteria(self, criteria: dict[str, Any], **kwargs) -> list[dict[str, Any]]:
        """
        Apply arbitrary filtering criteria to search results.
        
        Args:
            criteria (dict[str, Any]): Dictionary of field-value pairs to filter by.
            **kwargs: Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: The filtered search results.
        """
        assert isinstance(criteria, dict), f"Criteria must be a dictionary, got {type_name(criteria)}"

        query = kwargs.get("query", "")
        size = kwargs.get("size", 10)

        assert isinstance(query, str), f"Query must be a string, got {type_name(query)}"
        assert isinstance(size, int), f"Size must be an integer, got {type_name(size)}"
        assert size > 0, f"Size must be a positive integer, got {size}"

        # Build the Elasticsearch query
        query = query.strip()
        search_body = {
            "query": {"bool": {"must": [], "filter": []}},
            "size": size
        }

        # If a text query is provided, add it to the must clause
        if query:
            search_body["query"]["bool"]["must"].append({"match": {"text": query}})

        # Add filter criteria
        for field, value in criteria.items():
            assert isinstance(field, str), f"Field names must be strings, got {type_name(field)}"
            filter = None
            match value:
                case list(): 
                    filter = "terms"
                case dict() if ('gte' in value or 'lte' in value or 'gt' in value or 'lt' in value):
                    filter = "range"
                case _:
                    filter = "term"
            assert filter is not None, f"Unsupported filter type for field '{field}' with value '{value}'"
            search_body["query"]["bool"]["filter"].append({filter: {field: value}})

        try:
            self._execute_search(query, search_body, kwargs=kwargs)
        except Exception as e:
            raise e

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
        default_operator = kwargs.get("operator", "OR")
        fuzziness = kwargs.get("fuzziness", "AUTO")
        size = kwargs.get("size", 10)
        fields = kwargs.get("fields", ["text^3", "title^2", "content", "description"])

        assert isinstance(query, str), f"Query must be a string, got {type_name(query)}"
        assert isinstance(default_operator, str), f"Operator must be a string, got {type_name(default_operator)}"
        assert default_operator in ["AND", "OR"], f"Operator must be 'AND' or 'OR', got {default_operator}"
        assert isinstance(fuzziness, (str, int)), f"Fuzziness must be a string or integer, got {type_name(fuzziness)}"
        if isinstance(fuzziness, str):
            assert fuzziness == "AUTO", f"Fuzziness string must be 'AUTO', got {fuzziness}"

        # Process the query
        processed_query = self.parse_query(query, *args, **kwargs)
        if not processed_query:
            return []

        # Build the search body
        search_body = {
            "query": {
                "query_string": {
                    "query": processed_query,
                    "fields": fields,
                    "default_operator": default_operator,
                    "fuzziness": fuzziness
                }
            },
            "size": size
        }

        # Execute the search
        try:
            self._execute_search(query, search_body, kwargs=kwargs)
        except Exception as e:
            raise e

    def search(self, index: str, body: dict[str, Any]) -> ObjectApiResponse:
        """Perform a raw search query against the Elasticsearch index."""
        return self.client.search(index=index, body=body)

    def index(self, index: str, document: Mapping[str, Any]) -> ObjectApiResponse:
        """Index a document into the specified Elasticsearch index."""
        return self.client.index(index=index, document=document)

    def delete(self, index: str, id: str) -> ObjectApiResponse:
        """Delete a document from the specified Elasticsearch index by ID."""
        return self.client.delete(index=index, id=id)