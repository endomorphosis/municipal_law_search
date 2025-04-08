# get_embedding_and_calculate_cosine_similarity.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/get_embedding_and_calculate_cosine_similarity.py`

## Table of Contents

### Functions

- [`get_embedding_and_calculate_cosine_similarity`](#get_embedding_and_calculate_cosine_similarity)

## Functions

## `get_embedding_and_calculate_cosine_similarity`

```python
def get_embedding_and_calculate_cosine_similarity(embedding_data, query_embedding)
```

Calculate the cosine similarity between a query embedding and a given embedding.

**Parameters:**

- `embedding_data (dict[str, str])` (`Any`): A dictionary containing the embedding_cid and cid.
query_embedding (list[float], optional): The embedding vector for the query.

**Returns:**

- `Optional[tuple[(str, float)]]`: A tuple containing the CID and similarity score if the
                                cosine similarity exceeds the threshold, otherwise None.
