# app.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/app.py`

## Table of Contents

### Functions

- [`_get_html_for_this_citation`](#_get_html_for_this_citation)
- [`_fallback_search`](#_fallback_search)
- [`make_query_hash_table`](#make_query_hash_table)
- [`make_stats_table`](#make_stats_table)

### Classes

- [`HtmlRow`](#htmlrow)
- [`CitationsRow`](#citationsrow)
- [`EmbeddingsRow`](#embeddingsrow)
- [`SearchResponse`](#searchresponse)
- [`LawItem`](#lawitem)
- [`LLMAskRequest`](#llmaskrequest)
- [`LLMSearchEmbeddingsRequest`](#llmsearchembeddingsrequest)
- [`LLMCitationAnswerRequest`](#llmcitationanswerrequest)
- [`ErrorResponse`](#errorresponse)
- [`SqlQueryResponse`](#sqlqueryresponse)

## Functions

## `_get_html_for_this_citation`

```python
def _get_html_for_this_citation(row)
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

## `_fallback_search`

```python
def _fallback_search(query, per_page, offset)
```

Fallback to standard search if LLM not used or SQL failed

## `make_query_hash_table`

```python
def make_query_hash_table()
```

Create a hash table for the citation database.
NOTE: query_cid is made from the hash of the query string.

## `make_stats_table`

```python
def make_stats_table()
```

Create a stats table for the citation database.

## Classes

## `HtmlRow`

```python
class HtmlRow(BaseModel)
```

A Pydantic model representing a row in the 'html' table in html.db and american_law.db.

## `CitationsRow`

```python
class CitationsRow(BaseModel)
```

A Pydantic model representing a row in the 'citations' table in citations.db and american_law.db.

## `EmbeddingsRow`

```python
class EmbeddingsRow(BaseModel)
```

A Pydantic model representing a row in the 'embeddings' table in embeddings.db and american_law.db.

## `SearchResponse`

```python
class SearchResponse(BaseModel)
```

## `LawItem`

```python
class LawItem(BaseModel)
```

## `LLMAskRequest`

```python
class LLMAskRequest(BaseModel)
```

## `LLMSearchEmbeddingsRequest`

```python
class LLMSearchEmbeddingsRequest(BaseModel)
```

## `LLMCitationAnswerRequest`

```python
class LLMCitationAnswerRequest(BaseModel)
```

## `ErrorResponse`

```python
class ErrorResponse(BaseModel)
```

## `SqlQueryResponse`

```python
class SqlQueryResponse(BaseModel)
```
