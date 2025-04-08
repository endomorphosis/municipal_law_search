# error_response.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/schemas/error_response.py`

## Module Description

Error response schema for the American Law Search API.

This module defines the standardized structure for error responses
returned by the API endpoints when exceptions occur.

## Table of Contents

### Classes

- [`ErrorResponse`](#errorresponse)

## Classes

## `ErrorResponse`

```python
class ErrorResponse(BaseModel)
```

Standard error response model for API error handling.

This model is used to provide consistent error responses across all API endpoints.
It follows the common pattern of providing a human-readable error message in the
detail field.
