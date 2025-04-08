# law_item.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/schemas/law_item.py`

## Module Description

Law item schema for the American Law Search API.

This module defines the data structure for law items returned by the
API's search and retrieval endpoints. It represents a single legal document
from the municipal and county law corpus.

## Table of Contents

### Classes

- [`LawItem`](#lawitem)

## Classes

## `LawItem`

```python
class LawItem(BaseModel)
```

Represents a single legal document item from municipal or county law.

This model encapsulates all the information about a legal document, including
its metadata (citation information, jurisdiction, date) and the actual content
in HTML format. It's used as the primary response type for law search and 
retrieval endpoints.
