# format_initial_sql_return_from_search.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/app/search/format_initial_sql_return_from_search.py`

## Table of Contents

### Functions

- [`format_initial_sql_return_from_search`](#format_initial_sql_return_from_search)

## Functions

## `format_initial_sql_return_from_search`

```python
def format_initial_sql_return_from_search(row)
```

Format a database query result row into a standardized dictionary format.

This function takes a row from a database query result (as a dictionary) and formats it into a
standardized structure containing law information. If any of the specified keys are not present
in the input dictionary, they will default to "NA" in the output dictionary.

**Parameters:**

- `row (dict)` (`Any`): A dictionary representing a row from a database query result.

**Returns:**

- `dict`: A formatted dictionary with the following keys:
        - cid (str): Law ID
        - bluebook_cid (str): Bluebook citation ID
        - title (str): Title of the law
        - chapter (str): Chapter information
        - place_name (str): Name of the place associated with the law
        - state_name (str): Name of the state associated with the law
        - bluebook_citation (str): Formatted Bluebook citation
        - html (str, optional): HTML content if available
