# get_cid.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/common/get_cid.py`

## Table of Contents

### Functions

- [`_get_cid_for_string`](#_get_cid_for_string)
- [`get_cid`](#get_cid)

### Classes

- [`IpfsMultiformats`](#ipfsmultiformats)

## Functions

## `_get_cid_for_string`

```python
def _get_cid_for_string(string)
```

Generate a Content Identifier (CID) for a given string using SHA-256 hashing and multihash encoding.

**Parameters:**

- `string (str)` (`Any`): The input string for which the CID is to be generated.

**Returns:**

- `str`: The generated CID in base32 format.

## `get_cid`

```python
def get_cid(file_data, for_string)
```

Generate a Content Identifier (CID) for the given file or string.

For file paths, it directly calculates the CID. For strings, calculates the CID from a temporary file.

**Parameters:**

- `file_data (str | Path | bytes)` (`Any`): The file path or string data to generate a CID for.
for_string (bool): Flag to indicate if the input is an arbitrary string
(as opposed to a Path or the string of a path). Defaults to False.

**Returns:**

- `str`: The generated CID as a string.

## Classes

## `IpfsMultiformats`

```python
class IpfsMultiformats(object)
```

A class to manage Content Identifiers (CIDs) using multihash and IPFS standards.

This class provides methods to generate CIDs for files and content using the

**Methods:**

- [`get_cid`](#ipfsmultiformatsget_cid)
- [`get_file_sha256`](#ipfsmultiformatsget_file_sha256)
- [`get_multihash_sha256`](#ipfsmultiformatsget_multihash_sha256)

### `get_cid`

```python
def get_cid(self, file_data)
```

Generate a Content Identifier (CID) for the given file path or raw data.

For file paths, it directly calculates the CID. For raw data, it creates a temporary file,
writes the data to it, calculates the CID, and then removes the temporary file.

**Parameters:**

- `file_data (str | bytes)` (`Any`): The file path or raw data to generate a CID for.

**Returns:**

- `str`: The generated CID as a string.

### `get_file_sha256`

```python
def get_file_sha256(self, file_path)
```

Calculate the SHA-256 hash of a file. 

This method reads the file in 8192-byte chunks to handle large files
without loading everything into memory all at once.

**Parameters:**

- `file_path (str)` (`Any`): The path to the file to be hashed.

**Returns:**

- `bytes`: The SHA-256 hash of the file content.

### `get_multihash_sha256`

```python
def get_multihash_sha256(self, file_content_hash)
```

Wrap the given SHA-256 hash in Multihash format.

This method uses the 'sha2-256' algorithm identifier for the Multihash format.

**Parameters:**

- `file_content_hash (bytes)` (`Any`): The SHA-256 hash of the file content.

**Returns:**

- `bytes`: The Multihash-formatted hash.
