# fix_parquet_files_in_parallel.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/api/database/fix_parquet_files_in_parallel.py`

## Table of Contents

### Functions

- [`_get_rid_of_index_level_0_columns`](#_get_rid_of_index_level_0_columns)
- [`_fix_parquet`](#_fix_parquet)
- [`_make_unique_cid_out_of_embedding_and_foreign_cid`](#_make_unique_cid_out_of_embedding_and_foreign_cid)
- [`_add_gnis_column`](#_add_gnis_column)
- [`_drop_duplicates_based_on_cid_and_keep_the_first_occurrence`](#_drop_duplicates_based_on_cid_and_keep_the_first_occurrence)
- [`_drop_duplicates_based_on_bluebook_cid_and_keep_the_first_occurrence`](#_drop_duplicates_based_on_bluebook_cid_and_keep_the_first_occurrence)
- [`_fix_citation_parquet`](#_fix_citation_parquet)
- [`_fix_embeddings_parquet`](#_fix_embeddings_parquet)
- [`_fix_html_parquet`](#_fix_html_parquet)
- [`fix_parquet_files_in_parallel`](#fix_parquet_files_in_parallel)

## Functions

## `_get_rid_of_index_level_0_columns`

```python
def _get_rid_of_index_level_0_columns(df)
```

## `_fix_parquet`

```python
def _fix_parquet(file, funcs)
```

## `_make_unique_cid_out_of_embedding_and_foreign_cid`

```python
def _make_unique_cid_out_of_embedding_and_foreign_cid(df)
```

## `_add_gnis_column`

```python
def _add_gnis_column(df, gnis)
```

## `_drop_duplicates_based_on_cid_and_keep_the_first_occurrence`

```python
def _drop_duplicates_based_on_cid_and_keep_the_first_occurrence(df)
```

## `_drop_duplicates_based_on_bluebook_cid_and_keep_the_first_occurrence`

```python
def _drop_duplicates_based_on_bluebook_cid_and_keep_the_first_occurrence(df)
```

## `_fix_citation_parquet`

```python
def _fix_citation_parquet(file)
```

Get rid of any duplicate entries in the citation parquet files.

## `_fix_embeddings_parquet`

```python
def _fix_embeddings_parquet(file)
```

Re-generate embedding_cid based on the embedding and foreign cid.

## `_fix_html_parquet`

```python
def _fix_html_parquet(file)
```

Get rid of any duplicate entries in the citation parquet files.

## `fix_parquet_files_in_parallel`

```python
def fix_parquet_files_in_parallel(parquet_type)
```
