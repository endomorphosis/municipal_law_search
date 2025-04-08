# upload_to_hugging_face_in_parallel.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/database/upload_to_hugging_face_in_parallel.py`

## Module Description

Utility for parallel uploads to Hugging Face datasets repository.

This module provides functionality to efficiently upload multiple
folders of data to a Hugging Face dataset repository in parallel.

## Table of Contents

### Classes

- [`UploadToHuggingFaceInParallel`](#uploadtohuggingfaceinparallel)

## Classes

## `UploadToHuggingFaceInParallel`

```python
class UploadToHuggingFaceInParallel(object)
```

A class for uploading multiple folders to Hugging Face in parallel.

This class provides methods to efficiently upload multiple directories
to a Hugging Face dataset repository using parallel execution to
maximize throughput.

**Constructor Parameters:**

- `resources` (`Optional[dict]`): Optional dictionary of resources
configs: Configuration object containing Hugging Face credentials

**Methods:**

- [`_setup_hugging_face_api`](#uploadtohuggingfaceinparallel_setup_hugging_face_api)
- [`main`](#uploadtohuggingfaceinparallelmain)

### `_setup_hugging_face_api`

```python
def _setup_hugging_face_api(self, self)
```

Set up the Hugging Face API connection with authentication.

This method logs in to the Hugging Face API using the access token
from the configuration.

### `main`

```python
def main(self, output_dir, target_dir_name, file_path_ending)
```

Main entry point to upload files to Hugging Face in parallel.

This is a convenience method that formats the file path ending
pattern and calls the upload_to_hugging_face_in_parallel method.

**Parameters:**

- `output_dir` (`Path`): Base directory containing subdirectories to upload
target_dir_name: Target directory name in the Hugging Face repository
file_path_ending: File pattern for matching files to upload

**Returns:**

- `None`: None

**Examples:**

```python
```python
    uploader = UploadToHuggingFaceInParallel(configs=app_configs)
    uploader.main(
        output_dir=Path("/path/to/data"),
        target_dir_name="processed_data",
        file_path_ending=".parquet"
    )
    ```
```
