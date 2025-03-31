# make_dir_if_it_doesnt_exist.py: last updated 03:25 PM on March 31, 2025

**File Path:** `utils/make_dir_if_it_doesnt_exist.py`

## Table of Contents

### Functions

- [`make_dir_if_it_doesnt_exist`](#make_dir_if_it_doesnt_exist)

## Functions

## `make_dir_if_it_doesnt_exist`

```python
def make_dir_if_it_doesnt_exist(dir_path)
```

Creates a directory if it doesn't exist.

This function checks if the specified directory path exists and creates it if it doesn't.
It also validates that the directory is within the program's root directory for security.

**Parameters:**

- `dir_path (Path)` (`Any`): The path of the directory to create.

**Returns:**

- `None`: None

**Raises:**

- `ValueError`: If the directory path is not within the program's root directory
or is not the root directory itself.

**Examples:**

```python
>>> make_dir_if_it_doesnt_exist(Path('/path/to/directory'))
    # Creates the directory if it doesn't exist
```
