# load_prompt_from_yaml.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/llm/load_prompt_from_yaml.py`

## Table of Contents

### Functions

- [`load_prompt_from_yaml`](#load_prompt_from_yaml)

### Classes

- [`PromptFields`](#promptfields)
- [`LLMSettings`](#llmsettings)
- [`Prompt`](#prompt)

## Functions

## `load_prompt_from_yaml`

```python
def load_prompt_from_yaml(prompt_name, override, **kwargs)
```

Load a prompt from a YAML file and format it with provided values.

This function reads a prompt template from a YAML file located in the configured
prompts directory, validates it against the Prompt model, and formats it using
the provided keyword arguments.

**Parameters:**

- `prompt_name (str)` (`Any`): Name of the prompt file without the .yaml extension
**kwargs: Variable keyword arguments used to format the prompt template

**Returns:**

- `Prompt`: A validated and formatted Prompt object ready for use

**Raises:**

- `FileNotFoundError`: If the specified prompt file doesn't exist
ValidationError: If the YAML content doesn't match the Prompt model structure

**Examples:**

```python
>>> system_prompt = load_prompt_from_yaml("system_prompt", model_name="gpt-4")
```

## Classes

## `PromptFields`

```python
class PromptFields(BaseModel)
```

A Pydantic model for a prompt field structure for LLM interactions.

## `LLMSettings`

```python
class LLMSettings(BaseModel)
```

A Pydantic model for LLM settings.

## `Prompt`

```python
class Prompt(BaseModel)
```

A pydantic class for a prompt for LLM interactions.

**Methods:**

- [`messages`](#promptmessages) (property)
- [`safe_format`](#promptsafe_format)

### `messages`

```python
def messages(self, self)
```

Converts the prompt to OpenAI API format.

**Returns:**

- `dict`: A dictionary formatted for OpenAI API.

### `safe_format`

```python
def safe_format(self, **kwargs)
```
