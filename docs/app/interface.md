# interface.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/api/llm/interface.py`

## Module Description

API interface for the LLM integration with the American Law dataset.
Provides access to OpenAI-powered legal research and RAG components.

## Table of Contents

### Functions

- [`_validate_and_correct_sql_query_string`](#_validate_and_correct_sql_query_string)

### Classes

- [`LLMInterface`](#llminterface)

## Functions

## `_validate_and_correct_sql_query_string`

```python
def _validate_and_correct_sql_query_string(sql_query, fix_broken_queries)
```

Validate and correct a SQL query string.

**Parameters:**

- `sql_query` (`str`): The SQL query string to validate

**Returns:**

- `Optional[str]`: True if valid, False otherwise

## Classes

## `LLMInterface`

```python
class LLMInterface(object)
```

Interface for interacting with OpenAI LLM capabilities for the American Law dataset.
Provides a simplified API for accessing embeddings search and RAG functionality.

**Constructor Parameters:**

- `api_key` (`Optional[str]`): OpenAI API key
model: OpenAI model to use
embedding_model: OpenAI embedding model to use
data_path: Path to the American Law dataset files
db_path: Path to the SQLite database

**Methods:**

- [`_generic_response`](#llminterface_generic_response)
- [`ask_question`](#llminterfaceask_question)
- [`determine_user_intent`](#llminterfacedetermine_user_intent)
- [`generate_citation_answer`](#llminterfacegenerate_citation_answer)
- [`query_to_sql`](#llminterfacequery_to_sql)
- [`search_embeddings`](#llminterfacesearch_embeddings)

### `_generic_response`

```python
def _generic_response(self, message, system_prompt)
```

### `ask_question`

```python
def ask_question(self, query, use_rag, use_embeddings, document_limit, custom_system_prompt)
```

Ask a question about American law.

**Parameters:**

- `query` (`str`): User's question
use_rag: Whether to use Retrieval Augmented Generation
use_embeddings: Whether to use embeddings search for RAG
document_limit: Maximum number of context documents to include
custom_system_prompt: Custom system prompt for LLM

**Returns:**

- `Dict[(str, Any)]`: Dictionary with the generated response and additional information

### `determine_user_intent`

```python
def determine_user_intent(self, message)
```

Determine the user's intent based on the query.

**Parameters:**

- `query` (`Any`): User's input query

**Returns:**

- `str`: Intent type as a string

### `generate_citation_answer`

```python
def generate_citation_answer(self, query, citation_codes, system_prompt)
```

Generate an answer to a question with specific citation references.

**Parameters:**

- `query` (`str`): User's question
citation_codes: List of citation codes to use as context
system_prompt: Custom system prompt

**Returns:**

- `Dict[(str, Any)]`: Dictionary with the generated response and additional information

### `query_to_sql`

```python
def query_to_sql(self, query, custom_system_prompt)
```

Convert a natural language query into a PostgreSQL command for searching the American Law database.

**Parameters:**

- `query` (`str`): User's plaintext query
custom_system_prompt: Optional custom system prompt for the SQL generation

**Returns:**

- `Dict[(str, Any)]`: Dictionary with the generated SQL query and additional information

### `search_embeddings`

```python
def search_embeddings(self, query, file_id, top_k)
```

Search for relevant documents using embeddings.

**Parameters:**

- `query` (`str`): Search query
file_id: Optional file ID to limit search to
top_k: Number of top results to return

**Returns:**

- `List[Dict[(str, Any)]]`: List of relevant documents with similarity scores
