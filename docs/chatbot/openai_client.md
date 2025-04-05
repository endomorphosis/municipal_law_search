# openai_client.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/api/llm/openai_client.py`

## Module Description

OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.

## Table of Contents

### Functions

- [`_calc_cost`](#_calc_cost)
- [`calculate_cost`](#calculate_cost)

### Classes

- [`LLMOutput`](#llmoutput)
- [`LLMInput`](#llminput)
- [`LLMEngine`](#llmengine)
- [`OpenAIClient`](#openaiclient)

## Functions

## `_calc_cost`

```python
def _calc_cost(x, cost_per_1M)
```

## `calculate_cost`

```python
def calculate_cost(prompt, data, output, model)
```

## Classes

## `LLMOutput`

```python
class LLMOutput(BaseModel)
```

**Methods:**

- [`cost`](#llmoutputcost) (property)
- [`parsed_llm_response`](#llmoutputparsed_llm_response) (property)

### `cost`

```python
def cost(self, self)
```

### `parsed_llm_response`

```python
def parsed_llm_response(self, self)
```

## `LLMInput`

```python
class LLMInput(BaseModel)
```

**Methods:**

- [`embedding`](#llminputembedding) (property)
- [`response`](#llminputresponse) (property)

### `embedding`

```python
def embedding(self, self)
```

Generate an embedding for the user's message.

**Parameters:**

- `text` (`Any`): Text string to generate an embedding for

**Returns:**

- `List[float]`: Embedding vector

### `response`

```python
def response(self, self)
```

## `LLMEngine`

```python
class LLMEngine(BaseModel)
```

## `OpenAIClient`

```python
class OpenAIClient(object)
```

Client for OpenAI API integration with RAG capabilities for the American Law dataset.
Handles embeddings integration and semantic search against the law database.

**Constructor Parameters:**

- `api_key` (`str`): OpenAI API key (defaults to OPENAI_API_KEY env variable)
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

### `generate_rag_response`

```python
def generate_rag_response(self, query, use_embeddings, top_k, system_prompt)
```

Generate a response using RAG (Retrieval Augmented Generation).

**Parameters:**

- `query` (`str`): User query
use_embeddings: Whether to use embeddings for search
top_k: Number of context documents to include
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

Query the database for relevant laws using DuckDB.

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
