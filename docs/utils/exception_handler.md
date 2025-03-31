# exception_handler.py: last updated 03:25 PM on March 31, 2025

**File Path:** `utils/exception_handler.py`

## Table of Contents

### Functions

- [`exception_handler`](#exception_handler)

## Functions

## `exception_handler`

```python
def exception_handler(exception_type, exception, traceback, debug_hook)
```

Handle exceptions based on the configured log level.

This function provides a custom exception handler that either prints a simplified error
message or calls the default exception hook based on the log level.

**Parameters:**

- `exception_type` (`Any`): The type of the raised exception.
exception: The exception instance that was raised.
traceback: The traceback object.
debug_hook: The original exception hook to use when in debug mode. Defaults to sys.excepthook.

**Returns:**

- `Any`: None
