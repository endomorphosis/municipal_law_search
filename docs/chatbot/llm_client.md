# llm_client.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/api/llm/llm_client.py`

## Module Description

OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.

## Table of Contents

### Functions

- [`calculate_llm_api_cost`](#calculate_llm_api_cost)

### Classes

- [`AsyncLLMInput`](#asyncllminput)
- [`AsyncLLMOutput`](#asyncllmoutput)
- [`LLMOutput`](#llmoutput)
- [`OpenAiClient`](#openaiclient)
- [`AsyncLLMClient`](#asyncllmclient)

## Functions

## `calculate_llm_api_cost`

```python
def calculate_llm_api_cost(prompt, data, out, model)
```

## Classes

## `AsyncLLMInput`

```python
class AsyncLLMInput(BaseModel)
```

## `AsyncLLMOutput`

```python
class AsyncLLMOutput(BaseModel)
```

**Methods:**

- [`cost`](#asyncllmoutputcost) (property)

### `cost`

```python
def cost(self, self)
```

## `LLMOutput`

```python
class LLMOutput(BaseModel)
```

**Methods:**

- [`cost`](#llmoutputcost) (property)
- [`response`](#llmoutputresponse)

### `cost`

```python
def cost(self, self)
```

### `response`

```python
def response(self, self)
```

## `OpenAiClient`

```python
class OpenAiClient(object)
```

**Constructor Parameters:**

- `resources` (`dict`): Dictionary of resources for embeddings and database queries
configs: Configuration object

**Methods:**

- [`get_embeddings`](#openaiclientget_embeddings)
- [`get_response`](#openaiclientget_response)

### `get_embeddings`

```python
def get_embeddings(self, texts)
```

### `get_response`

```python
def get_response(self, user_message, system_prompt)
```

## `AsyncLLMClient`

```python
class AsyncLLMClient(object)
```

Asynchronous client for LLM API integration with RAG capabilities.
Handles embeddings integration and semantic search against the law database.

**Constructor Parameters:**

- `api_key` (`str`): OpenAI API key (defaults to OPENAI_API_KEY env variable)
model: OpenAI model to use for completion/chat
embedding_model: OpenAI model to use for embeddings
embedding_dimensions: Dimensions of the embedding vectors
temperature: Temperature setting for LLM responses
max_tokens: Maximum tokens for LLM responses
configs: Configuration object

**Methods:**

- [`execute_sql_query`](#asyncllmclientexecute_sql_query)

### `execute_sql_query`

```python
def execute_sql_query(self, query, raise_on_e)
```
