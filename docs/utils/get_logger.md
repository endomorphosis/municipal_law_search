# get_logger.py: last updated 03:25 PM on March 31, 2025

**File Path:** `utils/get_logger.py`

## Table of Contents

### Functions

- [`get_logger`](#get_logger)

## Functions

## `get_logger`

```python
def get_logger(name, log_file, level, max_size, backup_count)
```

Sets up a logger with both file and console handlers.

**Parameters:**

- `name` (`str`): Name of the logger.
log_file: Name of the log file. Defaults to 'app.log'.
level: Logging level. Defaults to logging.DEBUG.
max_size: Maximum size of the log file before it rotates. Defaults to 5MB.
backup_count: Number of backup files to keep. Defaults to 3.

**Returns:**

- `logging.Logger`: Configured logger.

**Examples:**

```python
# Usage
    logger = setup_logger(__name__)
```
