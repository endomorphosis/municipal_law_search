# get_hashes_from_hashes_csv.py: last updated 03:25 PM on March 31, 2025

**File Path:** `utils/get_hashes_from_hashes_csv.py`

## Table of Contents

### Functions

- [`get_hashes_from_hashes_csv`](#get_hashes_from_hashes_csv)

## Functions

## `get_hashes_from_hashes_csv`

```python
def get_hashes_from_hashes_csv(dir)
```

Reads hashes from a CSV file in the specified directory.

This function reads a file named 'hashes.csv' from the given directory,
extracts each line, and returns a list of hashes with whitespace stripped.

**Parameters:**

- `dir (Path)` (`Any`): The directory containing the 'hashes.csv' file.

**Returns:**

- `list[str]`: A list of hash strings with whitespace stripped.

**Examples:**

```python
>>> get_hashes_from_hashes_csv(Path("/path/to/directory"))
    ['hash1', 'hash2', 'hash3']
```
