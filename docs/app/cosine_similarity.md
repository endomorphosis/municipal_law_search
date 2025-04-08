# cosine_similarity.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/llm/cosine_similarity.py`

## Table of Contents

### Functions

- [`cosine_similarity`](#cosine_similarity)

## Functions

## `cosine_similarity`

```python
def cosine_similarity(x, y)
```

Calculate cosine similarity between two vectors.

**Parameters:**

- `x` (`list[float]`): First vector
y: Second vector

**Returns:**

- `float`: Cosine similarity score, ranging from -1 to 1.
        - 1 indicates identical vectors, 
        - 0 indicates orthogonal (e.g. perpendicular) vectors
        - -1 indicates opposite vectors.
