# app.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/app.py`

## Table of Contents

### Classes

- [`SearchFunction`](#searchfunction)

## Classes

## `SearchFunction`

```python
class SearchFunction(object)
```

Core class for performing natural language searches on the American law database.

This class orchestrates the entire search process, including query transformation,
database access, embedding similarity calculations, and result caching. It uses
a language model to convert natural language queries into SQL and supports both
cached search responses and live searches with streaming results.

**Constructor Parameters:**

- `search_query` (`str`): The natural language search query
llm: The language model interface for query translation
resources: Dictionary of utility functions and resources
configs: Application configuration

**Methods:**

- [`_calc_total_pages`](#searchfunction_calc_total_pages) (static method)
- [`close_cursor_and_connection`](#searchfunctionclose_cursor_and_connection)
- [`estimate_the_total_count_without_pagination`](#searchfunctionestimate_the_total_count_without_pagination)
- [`execute_the_actual_query_with_pagination`](#searchfunctionexecute_the_actual_query_with_pagination)
- [`format_search_response`](#searchfunctionformat_search_response)
- [`get_cached_query_results`](#searchfunctionget_cached_query_results)
- [`get_data_from_sql`](#searchfunctionget_data_from_sql)
- [`sort_and_save_search_query_results`](#searchfunctionsort_and_save_search_query_results)

### `_calc_total_pages`

```python
@staticmethod
def _calc_total_pages(total, per_page)
```

Calculate the total number of pages based on total results and page size.

This utility method calculates how many pages are needed to display all
results given the total number of results and the number of results per page.
It uses the ceiling division formula to ensure that any partial page at the
end is counted as a full page.

**Parameters:**

- `total` (`int`): The total number of results
per_page: The number of results per page

**Returns:**

- `int`: The total number of pages needed

**Examples:**

```python
>>> _calc_total_pages(101, 20)
    6  # 101 results with 20 per page = 5 full pages + 1 partial page
```

### `close_cursor_and_connection`

```python
def close_cursor_and_connection(self, self)
```

Closes the database cursor and connection.

This method ensures that all database resources are properly released,
preventing resource leaks. It should be called when the search operation
is complete or if an error occurs.

**Returns:**

- `None`: None

### `estimate_the_total_count_without_pagination`

```python
def estimate_the_total_count_without_pagination(self, sql_query)
```

Estimates the total count of records that would be returned by a SQL query.

This method calculates the total number of results that would be returned by
the given SQL query without pagination. This is used to determine the total
number of pages for pagination and to provide count information to the client.

**Parameters:**

- `sql_query` (`str`): The SQL query whose results we want to count

**Returns:**

- `int`: Total number of records that would be returned by the query

### `execute_the_actual_query_with_pagination`

```python
def execute_the_actual_query_with_pagination(self, sql_query)
```

Executes the SQL query with pagination and formats the initial results.

This method executes the given SQL query using the class cursor,
processes the results to avoid duplicates, and formats them using the
_format_initial_sql_return_from_search utility.

**Parameters:**

- `sql_query` (`str`): The SQL query to execute

**Returns:**

- `list[dict[(str, Any)]]`: Initial formatted results from the SQL query

### `format_search_response`

```python
def format_search_response(self, cumulative_results, page, per_page)
```

Format the search results into a standardized response structure.

This method takes the accumulated search results and formats them into a
standardized SearchResponse structure. It includes the results, pagination
information, and total counts to help the client properly display the results.

**Parameters:**

- `cumulative_results` (`list[dict]`): List of search result dictionaries
page: The current page number
per_page: The number of results per page

**Returns:**

- `dict`: The formatted search response as a dictionary

### `get_cached_query_results`

```python
def get_cached_query_results(self, page, per_page)
```

Retrieve previously cached search results for the current query.

This method checks if the current search query has been executed before and
if its results are stored in the search_query table. If found, it returns
the cached results with the appropriate pagination, avoiding the need for
a full search operation.

**Parameters:**

- `page` (`int`): The page number of results to retrieve (1-based)
per_page: The number of results per page

**Returns:**

- `dict[str, Any] | None`: The cached search results if found, otherwise None

**Raises:**

- `HTTPException`: If there is an error accessing the cache

### `get_data_from_sql`

```python
def get_data_from_sql(self, cursor, return_a, sql_query, how_many)
```

Execute a SQL query and return the results in the specified format.

This method is a wrapper around the _get_data_from_sql utility function,
providing a consistent interface for executing SQL queries and retrieving
results in various formats.

**Parameters:**

- `cursor` (`SqlCursor`): The database cursor to use for executing the query
return_a: The format to return results in ('dict', 'tuple', or 'df')
sql_query: The SQL query to execute
how_many: How many results to return (for 'tuple' format)

**Returns:**

- `list[dict[(str, Any)]]`: List of dictionaries, list of tuples, or a pandas DataFrame, depending on return_a

### `sort_and_save_search_query_results`

```python
def sort_and_save_search_query_results(self, self)
```

Sort the results by similarity score and save the top 100 to the database.

This method saves the search query, its embedding, and the top 100 results 
to the database for future use. This caching mechanism improves performance
for repeated or similar searches.

**Returns:**

- `None`: None
