# get_embedding_cids_for_all_the_cids.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/get_embedding_cids_for_all_the_cids.py`

## Table of Contents

### Functions

- [`get_embedding_cids_for_all_the_cids`](#get_embedding_cids_for_all_the_cids)

## Functions

## `get_embedding_cids_for_all_the_cids`

```python
def get_embedding_cids_for_all_the_cids(initial_results, batch_size)
```

Retrieves embedding CIDs for all the provided CIDs from the embeddings database.

**Parameters:**

- `initial_results (list[dict])` (`Any`): A list of dictionaries, where each dictionary contains
a 'cid' key representing the unique identifier.

**Returns:**

- `Generator[(None, None, list[dict])]`: A list of dictionaries, where each dictionary contains the 'embedding_cid'
                and 'cid' retrieved from the embeddings database.
