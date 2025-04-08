# sort_and_save_search_query_results.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/sort_and_save_search_query_results.py`

## Module Description

Utility for sorting search results by similarity score and saving them to cache.

This module provides functions for organizing search results by relevance
and caching them in the search_query table for future retrieval, which
improves performance for repeated searches.

## Table of Contents

### Functions

- [`sort_and_save_search_query_results`](#sort_and_save_search_query_results)

### Classes

- [`_SearchQuery`](#_searchquery)

## Functions

## `sort_and_save_search_query_results`

```python
def sort_and_save_search_query_results(search_query_cid, search_query, search_query_embedding, query_table_embedding_cids, total)
```

Sorts search results by similarity score and saves them to the search_query table.

This function takes a list of content IDs with their similarity scores, sorts them
by score, extracts the top 100 results, and saves them to the search_query table
along with the original query information. This creates a cache of search results
that can be reused for identical or similar future queries.

**Parameters:**

- `search_query_cid` (`str`): The content identifier for the search query
search_query: The original search query text
search_query_embedding: The vector embedding of the search query
query_table_embedding_cids: A list of tuples containing (content_id, similarity_score)
total: The total number of results found for this query

**Returns:**

- `None`: None

**Examples:**

```python
```python
    # After performing a search and calculating similarity scores
    sort_and_save_search_query_results(
        search_query_cid="bafkreihvwc5kg3estvqpicmmqghwiriti6mz5w3lk4k3app3guwk6onrq4",
        search_query="zoning laws in California",
        search_query_embedding=[0.1, 0.2, ...],  # 1536-dimensional vector
        query_table_embedding_cids=[
            ("bafkreiabc123", 0.92),
            ("bafkreidef456", 0.85),
            # ... more results with scores
        ],
        total=157
    )
    ```
```

## Classes

## `_SearchQuery`

```python
class _SearchQuery(BaseModel)
```

A Pydantic model representing a search query and its cached results.

This model stores a search query, its embedding vector, and the content IDs
of the top 100 most relevant results, enabling fast retrieval of previous
search results.

**Methods:**

- [`to_tuple`](#_searchqueryto_tuple)

### `to_tuple`

```python
def to_tuple(self, self)
```

Convert the Pydantic model to a tuple for database insertion.

**Returns:**

- `tuple`: A tuple containing all model fields in order for SQL insertion
