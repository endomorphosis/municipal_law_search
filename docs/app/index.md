# Python Documentation

## Files

### /home/kylerose1946/american_law_search/app

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [app.py](app.md): last updated 02:01 AM on April 08, 2025
- [configs.py](configs.md): last updated 02:01 AM on April 08, 2025
- [logger.py](logger.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/api/database

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [analyze_american_law_dataset.py](analyze_american_law_dataset.md): last updated 02:01 AM on April 08, 2025
- [create_american_law_db.py](create_american_law_db.md): last updated 02:01 AM on April 08, 2025
- [fix_parquet_files_in_parallel.py](fix_parquet_files_in_parallel.md): last updated 02:01 AM on April 08, 2025
- [setup_citation_db.py](setup_citation_db.md): last updated 02:01 AM on April 08, 2025
- [setup_embeddings_db.py](setup_embeddings_db.md): last updated 02:01 AM on April 08, 2025
- [setup_html_db.py](setup_html_db.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/api/database/implementations

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [duckdb.py](duckdb.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/api/llm

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [_test_db.py](_test_db.md): last updated 02:01 AM on April 08, 2025
- [async_interface.py](async_interface.md): last updated 02:01 AM on April 08, 2025
- [async_openai_client.py](async_openai_client.md): last updated 02:01 AM on April 08, 2025
- [constants.py](constants.md): last updated 02:01 AM on April 08, 2025
- [embeddings_utils.py](embeddings_utils.md): last updated 02:01 AM on April 08, 2025
- [interface.py](interface.md): last updated 02:01 AM on April 08, 2025
- [llm_client.py](llm_client.md): last updated 02:01 AM on April 08, 2025
- [openai_client.py](openai_client.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/api/llm/implementations

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [openai.py](openai.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/schemas

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [citation_row.py](citation_row.md): last updated 02:01 AM on April 08, 2025
- [embeddings_row.py](embeddings_row.md): last updated 02:01 AM on April 08, 2025
- [error_response.py](error_response.md): last updated 02:01 AM on April 08, 2025
- [html_row.py](html_row.md): last updated 02:01 AM on April 08, 2025
- [law_item.py](law_item.md): last updated 02:01 AM on April 08, 2025
- [search_response.py](search_response.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/tests

- [test_database_migration.py](test_database_migration.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/utils

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/utils/app

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [_get_a_database_connection.py](_get_a_database_connection.md): last updated 02:01 AM on April 08, 2025
- [_get_data_from_sql.py](_get_data_from_sql.md): last updated 02:01 AM on April 08, 2025
- [clean_html.py](clean_html.md): last updated 02:01 AM on April 08, 2025
- [close_database_cursor.py](close_database_cursor.md): last updated 02:01 AM on April 08, 2025
- [get_html_for_this_citation.py](get_html_for_this_citation.md): last updated 02:01 AM on April 08, 2025
- [get_law.py](get_law.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/utils/app/search

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [close_database_connection.py](close_database_connection.md): last updated 02:01 AM on April 08, 2025
- [estimate_the_total_count_without_pagination.py](estimate_the_total_count_without_pagination.md): last updated 02:01 AM on April 08, 2025
- [format_initial_sql_return_from_search.py](format_initial_sql_return_from_search.md): last updated 02:01 AM on April 08, 2025
- [get_cached_query_results.py](get_cached_query_results.md): last updated 02:01 AM on April 08, 2025
- [get_database_cursor.py](get_database_cursor.md): last updated 02:01 AM on April 08, 2025
- [get_embedding_and_calculate_cosine_similarity.py](get_embedding_and_calculate_cosine_similarity.md): last updated 02:01 AM on April 08, 2025
- [get_embedding_cids.py](get_embedding_cids.md): last updated 02:01 AM on April 08, 2025
- [llm_sql_output.py](llm_sql_output.md): last updated 02:01 AM on April 08, 2025
- [make_search_query_table_if_it_doesnt_exist.py](make_search_query_table_if_it_doesnt_exist.md): last updated 02:01 AM on April 08, 2025
- [sort_and_save_search_query_results.py](sort_and_save_search_query_results.md): last updated 02:01 AM on April 08, 2025
- [turn_english_into_sql.py](turn_english_into_sql.md): last updated 02:01 AM on April 08, 2025
- [type_vars.py](type_vars.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/utils/common

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [exception_handler.py](exception_handler.md): last updated 02:01 AM on April 08, 2025
- [get_cid.py](get_cid.md): last updated 02:01 AM on April 08, 2025
- [run_in_parallel_with_concurrency_limiter.py](run_in_parallel_with_concurrency_limiter.md): last updated 02:01 AM on April 08, 2025
- [run_in_process_pool.py](run_in_process_pool.md): last updated 02:01 AM on April 08, 2025
- [safe_format.py](safe_format.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/utils/database

- [get_db.py](get_db.md): last updated 02:01 AM on April 08, 2025
- [make_stats_table.py](make_stats_table.md): last updated 02:01 AM on April 08, 2025
- [upload_to_hugging_face_in_parallel.py](upload_to_hugging_face_in_parallel.md): last updated 02:01 AM on April 08, 2025

### /home/kylerose1946/american_law_search/app/utils/llm

- [__init__.py](__init__.md): last updated 02:01 AM on April 08, 2025
- [cosine_similarity.py](cosine_similarity.md): last updated 02:01 AM on April 08, 2025
- [load_prompt_from_yaml.py](load_prompt_from_yaml.md): last updated 02:01 AM on April 08, 2025
