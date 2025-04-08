# safe_format.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/common/safe_format.py`

## Table of Contents

### Functions

- [`handle_percent_format`](#handle_percent_format)
- [`safe_format`](#safe_format)

### Classes

- [`SafeFormatter`](#safeformatter)

## Functions

## `handle_percent_format`

```python
def handle_percent_format(format_string, *args, **kwargs)
```

Format a string using percent-style formatting. Only standard format specifiers (diouxXeEfFgGcrs%) are allowed for safety

**Parameters:**

- `format_string (str)` (`Any`): The string containing percent-style format specifiers
*args: Positional arguments to be used for positional percent formatting
**kwargs: Keyword arguments to be used for named parameter percent formatting

**Returns:**

- `str`: The formatted string after all substitutions are applied

**Examples:**

```python
>>> handle_percent_format("Hello, %s!", "world")
    'Hello, world!'
    >>> handle_percent_format("%(name)s is %(age)d years old", name="Alice", age=30)
    'Alice is 30 years old'
```

## `safe_format`

```python
def safe_format(format_string, *args, **kwargs)
```

Format a string safely, handling both brace-style ({}) and percent-style (%) formatting.

**Parameters:**

- `format_string` (`str`): The string to be formatted.
*args: Variable length argument list.
**kwargs: Arbitrary keyword arguments to be used in formatting.

**Returns:**

- `str`: A formatted string where keys from kwargs are substituted into the format_string.
    Missing keys are left as is in the resulting string.

**Examples:**

```python
>>> kwargs = {
>>>     "first": 1,
>>>     "second": "second",
>>>     "third": get_bool("three"),
>>>     "fourth": 2*2
>>> }
```

## Classes

## `SafeFormatter`

```python
class SafeFormatter(string.Formatter)
```

A custom string formatter that safely handles missing keys and invalid format strings.

This class extends the built-in string.Formatter to provide more robust formatting
capabilities, particularly when dealing with potentially missing keys or malformed
format strings.

**Methods:**

- [`get_value`](#safeformatterget_value)
- [`parse`](#safeformatterparse)

### `get_value`

```python
def get_value(self, key, args, kwargs)
```

Retrieve a value for a given key from kwargs, or return a placeholder if not found.

**Parameters:**

- `key` (`Any`): The key to look up in kwargs.
args: Positional arguments (not used in this implementation).
kwargs: Keyword arguments containing the values to format.

**Returns:**

- `Any`: The value associated with the key if found in kwargs, otherwise a placeholder
    string containing the key.

### `parse`

```python
def parse(self, format_string)
```

Parse the format string, handling potential ValueError exceptions.

**Parameters:**

- `format_string` (`Any`): The string to be parsed for formatting.

**Returns:**

- `Any`: A list of tuples representing the parsed format string. If parsing fails,
    returns a list with a single tuple containing the entire format string.
