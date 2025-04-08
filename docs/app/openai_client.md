# openai_client.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/api/llm/openai_client.py`

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

Calculate the cost of tokens based on the per-million token rate.

**Parameters:**

- `x (int)` (`Any`): Number of tokens
cost_per_1M (float): Cost per million tokens in USD

**Returns:**

- `float`: Cost in USD

## `calculate_cost`

```python
def calculate_cost(prompt, data, output, model)
```

Calculate the cost of an OpenAI API call based on input and output tokens.

This function calculates the cost of a completion or chat request by counting
tokens in the prompt, data, and output, then applying the appropriate pricing
for the specified model.

**Parameters:**

- `prompt (str)` (`Any`): The system prompt text
data (str): The user message/data text
output (str): The model's response text
model (str): The OpenAI model name (e.g., "gpt-4o", "gpt-3.5-turbo")

**Returns:**

- `Optional[float]`: The estimated cost in USD, or None if calculation failed

## Classes

## `LLMOutput`

```python
class LLMOutput(BaseModel)
```

Model representing the output from an LLM interaction.

This class encapsulates the response from an LLM, including the original input,
prompt, and provides utilities for cost calculation and response parsing.

**Methods:**

- [`cost`](#llmoutputcost) (property)
- [`parsed_llm_response`](#llmoutputparsed_llm_response) (property)

### `cost`

```python
def cost(self, self)
```

Calculate the cost of this LLM interaction.

**Returns:**

- `float`: The estimated cost in USD

### `parsed_llm_response`

```python
def parsed_llm_response(self, self)
```

Parse the LLM response using the provided parser function.

**Returns:**

- `Any`: The parsed response in the format determined by the parser

## `LLMInput`

```python
class LLMInput(BaseModel)
```

Model representing an input to an LLM for generating a response.

This class encapsulates all parameters needed for an LLM API call, including
the message, system prompt, and generation parameters. It also provides properties
that execute the LLM call and retrieve responses or embeddings.

**Methods:**

- [`embedding`](#llminputembedding) (property)
- [`response`](#llminputresponse) (property)

### `embedding`

```python
def embedding(self, self)
```

Generate an embedding vector for the user's message.

This property uses the OpenAI embeddings API to create a vector
representation of the user's message, which can be used for
semantic search or similarity comparison.

**Returns:**

- `List[float]`: The embedding vector or empty list if generation failed

### `response`

```python
def response(self, self)
```

Generate a response from the LLM using the configured parameters.

This property sends the user message and system prompt to the LLM API
and returns the structured response.

**Returns:**

- `Optional[LLMOutput]`: The structured LLM response or an error message string

## `LLMEngine`

```python
class LLMEngine(BaseModel)
```

Base model for LLM engine implementations.

This is a placeholder class that serves as a base for different LLM engine
implementations. It defines the basic interface for an LLM engine but
currently doesn't contain any functionality. Future implementations
will extend this class with specific engine capabilities.

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

This method retrieves relevant legal documents based on the query,
builds a context from them, and then generates a response using the LLM
with the retrieved context as additional information.

**Parameters:**

- `query (str)` (`Any`): User's query about legal information
use_embeddings (bool, optional): Whether to use embeddings for semantic search.
If False, will use text-based search instead. Defaults to True.
top_k (int, optional): Number of context documents to include. Defaults to 5.
system_prompt (Optional[str], optional): Custom system prompt to override
the default legal assistant prompt. Defaults to None.

**Returns:**

- `Dict[(str, Any)]`: Dictionary with the generated response and metadata:
        - query: The original query
        - response: The generated response text
        - context_used: List of citations for the documents used as context
        - model_used: The LLM model used
        - total_tokens: Total tokens used, or error message if generation failed

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
