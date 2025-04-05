# embeddings_utils.py: last updated 12:42 AM on April 05, 2025

**File Path:** `chatbot/api/llm/embeddings_utils.py`

## Module Description

Embeddings utilities for working with the American Law dataset.
Provides tools for loading, processing, and using embeddings from parquet files.

## Table of Contents

### Classes

- [`EmbeddingsManager`](#embeddingsmanager)

## Classes

## `EmbeddingsManager`

```python
class EmbeddingsManager(object)
```

Manager for embeddings data in the American Law dataset.
Handles loading, processing, and searching embeddings in parquet files.

**Constructor Parameters:**

- `configs` (`Optional[Configs]`): - data_path: Path to the dataset files
- db_path: Path to the SQLite database

**Methods:**

- [`cosine_similarity`](#embeddingsmanagercosine_similarity)
- [`get_db_connection`](#embeddingsmanagerget_db_connection)
- [`get_document_metadata`](#embeddingsmanagerget_document_metadata)
- [`list_embedding_files`](#embeddingsmanagerlist_embedding_files)
- [`load_embeddings`](#embeddingsmanagerload_embeddings)
- [`search_across_files`](#embeddingsmanagersearch_across_files)
- [`search_db_by_cid`](#embeddingsmanagersearch_db_by_cid)
- [`search_embeddings_in_file`](#embeddingsmanagersearch_embeddings_in_file)

### `cosine_similarity`

```python
def cosine_similarity(self, vec1, vec2)
```

Calculate cosine similarity between two vectors.

**Parameters:**

- `vec1` (`List[float]`): First vector
vec2: Second vector

**Returns:**

- `float`: Cosine similarity score

### `get_db_connection`

```python
def get_db_connection(self, self)
```

Get a connection to the SQLite database.

**Returns:**

- `Any`: SQLite connection

### `get_document_metadata`

```python
def get_document_metadata(self, cid, file_id)
```

Get metadata for a document from citation and HTML files.

**Parameters:**

- `cid` (`str`): Content ID
file_id: File ID

**Returns:**

- `Dict[(str, Any)]`: Document metadata

### `list_embedding_files`

```python
def list_embedding_files(self, self)
```

List all embedding files in the data path.

**Returns:**

- `List[str]`: List of embedding file paths

### `load_embeddings`

```python
def load_embeddings(self, file_id)
```

Load embeddings from a parquet file.

**Parameters:**

- `file_id` (`str`): ID of the file to load

**Returns:**

- `pd.DataFrame`: DataFrame with embeddings

### `search_across_files`

```python
def search_across_files(self, query_embedding, max_files, top_k)
```

Search for similar embeddings across multiple files.

**Parameters:**

- `query_embedding` (`List[float]`): Query embedding vector
max_files: Maximum number of files to search
top_k: Number of top results per file

**Returns:**

- `List[Dict[(str, Any)]]`: List of documents with similarity scores and metadata

### `search_db_by_cid`

```python
def search_db_by_cid(self, cid)
```

Search for a document in the database by content ID.

**Parameters:**

- `cid` (`str`): Content ID

**Returns:**

- `Dict[(str, Any)]`: Document data

### `search_embeddings_in_file`

```python
def search_embeddings_in_file(self, query_embedding, file_id, top_k)
```

Search for similar embeddings in a specific file.

**Parameters:**

- `query_embedding` (`List[float]`): Query embedding vector
file_id: ID of the file to search in
top_k: Number of top results to return

**Returns:**

- `List[Dict[(str, Any)]]`: List of documents with similarity scores
