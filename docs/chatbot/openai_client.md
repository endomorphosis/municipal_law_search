# openai_client.py: last updated 03:25 PM on March 31, 2025

**File Path:** `chatbot/api/llm/openai_client.py`

## Module Description

OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.

## Table of Contents

### Classes

- [`OpenAIClient`](#openaiclient)

## Classes

## `OpenAIClient`

```python
class OpenAIClient(object)
```

Client for OpenAI API integration with RAG capabilities for the American Law dataset.
Handles embeddings integration and semantic search against the law database.

**Constructor Parameters:**

- `api_key` (`Optional[str]`): OpenAI API key (defaults to OPENAI_API_KEY env variable)
model: OpenAI model to use for completion/chat
embedding_model: OpenAI model to use for embeddings
embedding_dimensions: Dimensions of the embedding vectors
temperature: Temperature setting for LLM responses
max_tokens: Maximum tokens for LLM responses
data_path: Path to the American Law dataset files
db_path: Path to the SQLite database

**Methods:**

- [`generate_rag_response`](#openaiclientgenerate_rag_response)
- [`get_embeddings`](#openaiclientget_embeddings)
- [`get_single_embedding`](#openaiclientget_single_embedding)
- [`query_database`](#openaiclientquery_database)
- [`search_embeddings`](#openaiclientsearch_embeddings)
- [`vector_similarity`](#openaiclientvector_similarity)

### `generate_rag_response`

```python
def generate_rag_response(self, query, use_embeddings, context_limit, system_prompt)
```

Generate a response using RAG (Retrieval Augmented Generation).

**Parameters:**

- `query` (`str`): User query
use_embeddings: Whether to use embeddings for search
context_limit: Number of context documents to include
system_prompt: Custom system prompt

**Returns:**

- `Dict[(str, Any)]`: Dictionary with the generated response and context used

### `get_embeddings`

```python
def get_embeddings(self, texts)
```

Generate embeddings for a list of text inputs using OpenAI's embedding model.

**Parameters:**

- `texts` (`List[str]`): List of text strings to generate embeddings for

**Returns:**

- `List[List[float]]`: List of embedding vectors

### `get_single_embedding`

```python
def get_single_embedding(self, text)
```

Generate an embedding for a single text input.

**Parameters:**

- `text` (`str`): Text string to generate an embedding for

**Returns:**

- `List[float]`: Embedding vector

### `query_database`

```python
def query_database(self, query, limit)
```

Query the SQLite database for relevant laws.

**Parameters:**

- `query` (`str`): Search query
limit: Maximum number of results to return

**Returns:**

- `List[Dict[(str, Any)]]`: List of matching law records

### `search_embeddings`

```python
def search_embeddings(self, query, gnis, top_k)
```

Search for relevant documents using embeddings.

**Parameters:**

- `query` (`str`): Search query
gnis: Optional file ID to limit search to
top_k: Number of top results to return

**Returns:**

- `List[Dict[(str, Any)]]`: List of relevant documents with similarity scores

### `vector_similarity`

```python
def vector_similarity(self, x, y)
```

Calculate cosine similarity between two vectors.

**Parameters:**

- `x` (`List[float]`): First vector
y: Second vector

**Returns:**

- `float`: Cosine similarity score
