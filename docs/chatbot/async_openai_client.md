# async_openai_client.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/api/llm/async_openai_client.py`

## Module Description

OpenAI Client implementation for American Law database.
Provides integration with OpenAI APIs and RAG components for legal research.

## Table of Contents

### Functions

- [`validate_prompt`](#validate_prompt)
- [`_load_prompt_from_yaml`](#_load_prompt_from_yaml)
- [`calculate_cost`](#calculate_cost)

### Classes

- [`PromptFields`](#promptfields)
- [`Prompt`](#prompt)
- [`AsyncLLMInput`](#asyncllminput)
- [`AsyncLLMOutput`](#asyncllmoutput)
- [`LLMOutput`](#llmoutput)
- [`AsyncOpenAIClient`](#asyncopenaiclient)

## Functions

## `validate_prompt`

```python
def validate_prompt(prompt)
```

## `_load_prompt_from_yaml`

```python
def _load_prompt_from_yaml(name, configs, **kwargs)
```

## `calculate_cost`

```python
def calculate_cost(prompt, data, out, model)
```

## Classes

## `PromptFields`

```python
class PromptFields(BaseModel)
```

## `Prompt`

```python
class Prompt(BaseModel)
```

**Methods:**

- [`safe_format`](#promptsafe_format)

### `safe_format`

```python
def safe_format(self, **kwargs)
```

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

## `AsyncOpenAIClient`

```python
class AsyncOpenAIClient(object)
```

Asynchronous client for OpenAI API integration with RAG capabilities for the American Law dataset.
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

