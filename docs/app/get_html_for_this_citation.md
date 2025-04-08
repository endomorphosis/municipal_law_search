# get_html_for_this_citation.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/get_html_for_this_citation.py`

## Table of Contents

### Functions

- [`get_html_for_this_citation`](#get_html_for_this_citation)

## Functions

## `get_html_for_this_citation`

```python
def get_html_for_this_citation(row)
```

Retrieves the HTML content associated with a given citation ID (cid) from the database.

**Parameters:**

- `row (dict | NamedTuple)` (`Any`): A data structure containing the citation ID (cid).
If `row` is a dictionary, the cid is accessed via `row['cid']`.
If `row` is a NamedTuple, the cid is accessed via `row.cid`.
read_only (bool): A flag indicating whether the database connection should be read-only.

**Returns:**

- `str`: The HTML content corresponding to the provided citation ID.
        If none is available, returns "Content not available".
