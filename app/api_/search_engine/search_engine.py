import asyncio
from collections import defaultdict
import contextlib
import functools
import logging
import re
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, AsyncContextManager, Callable, Optional


from configs import Configs
from read_only_database import Database


class DependencyError(RuntimeError):
    """
    Custom exception for handling dependency errors in the circuit breaker pattern.
    
    Attributes:
        message: Error message describing the dependency failure
        dependency: Name of the dependency that failed
    """
    def __init__(self, message: str):
        super().__init__(message)


class DependencyState(Enum):
    """
    Enum representing the state of a dependency in the circuit breaker pattern.
    
    Attributes:
        CLOSED: Circuit is closed, dependency is operational
        OPEN: Circuit is open, dependency is non-operational
        HALF_OPEN: Circuit is testing if dependency has recovered
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half-open"


class ErrorLevel(Enum):
    """
    Enum representing the severity level of errors.
    
    Attributes:
        LOW: Low severity error
        MEDIUM: Medium severity error
        HIGH: High severity error
        CRITICAL: Critical severity error
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


HOUR_IN_SECONDS = 3600
MINUTE_IN_SECONDS = 60
MILLISECOND_SCALAR = 1000



def now() -> float:
    """Get the current time in seconds since the epoch."""
    return time.monotonic()

def fallback(fallback_method_name: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            fallback_func = getattr(self, fallback_method_name, None)
            if not callable(fallback_func):
                raise ValueError(f"Fallback method '{fallback_method_name}' is not callable or does not exist.")
            primary_name = func.__name__

            if 'query' in kwargs:
                args[0] = kwargs.pop('query', '*')

            try:
                return await func(self, *args, **kwargs)
            except Exception as e:
                self.logger.exception(f"{primary_name} failed, trying {fallback_method_name}: {e}")
                try:
                    result = await fallback_func(*args, **kwargs)
                    self.track_dependency_failure(primary_name, recovered=True)
                    return result
                except Exception as fallback_error:
                    self.track_dependency_failure(primary_name, recovered=False)
                    raise DependencyError(f"Both {primary_name} and {fallback_method_name} failed") from fallback_error
        return wrapper
    return decorator


@contextlib.asynccontextmanager
async def timeit():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.monotonic()
            try:
                yield
            finally:
                self.calculate_duration_ms(start_time)
        return wrapper
    return decorator


def _type_check_str(query: Any) -> None:
    if not isinstance(query, str):
        raise TypeError(f"Query must be a string, got {type(query).__name__}")

def _value_check_str(query: str) -> None:
    if not query.strip():
        raise ValueError("Query cannot be empty or whitespace")


class SearchEngine:
    """
    An orchestration class to manage the logic for search operations and results.
    
    This class provides methods for performing searches and managing search results.
    It's designed to work with *any* search engine implementation
        (e.g. Elasticsearch, Apache Lucene, OpenSearch, etc.) through dependency injection.
    
    Attributes:
        configs: Configuration settings for the search engine
        resources: Dictionary of callable functions for search operations
        _text_search: Callable that performs the actual search operation.
        _db: Database instance for data retrieval
        _results: List of search results from the last search operation
        _error_count: Number of errors encountered
        _operation_count: Number of operations performed
        _dependency_failures: Dictionary tracking dependency failures
        _dependency_recovery: Dictionary tracking dependency recovery attempts
        _circuit_breakers: Dictionary tracking circuit breaker states for dependencies
        _design_query_volume: Expected peak query volume the system is designed to handle

    Methods:
        search(query: str, *args, **kwargs) -> list[dict[str, Any]]:
            Perform a search operation using the provided query.
        text_search(query: str, *args, **kwargs) -> list[dict[str, Any]]:
            Perform a text-based search operation.
        image_search(image_path: str, *args, **kwargs) -> list[dict[str, Any]]:
            Perform an image-based search operation.
        voice_search(audio_path: str, *args, **kwargs) -> list[dict[str, Any]]:
            Perform a voice-based search operation.
        exact_match(phrase: str, *args, **kwargs) -> list[dict[str, Any]]:
            Perform an exact phrase matching search.
        fuzzy_match(term: str, threshold: float = 0.8, *args, **kwargs) -> list[dict[str, Any]]:
            Perform a fuzzy matching search with configurable threshold.
        string_exclusion(include_term: str, exclude_term: str, *args, **kwargs) -> list[dict[str, Any]]:
            Perform a search that excludes specific terms.
        filter_criteria(criteria: dict[str, Any], *args, **kwargs) -> list[dict[str, Any]]:
            Apply arbitrary filtering criteria to search results.
        ranking_algorithm(query: str, results: list[dict[str, Any]], *args, **kwargs) -> list[dict[str, Any]]:
            Sort and rank search results based on relevance.
        multi_field_search(query: str, fields: list[str], weights: list[float] = None, *args, **kwargs) -> list[dict[str, Any]]:
            Search across multiple fields with configurable weights.
        query_parser(query: str, *args, **kwargs) -> str:
            Parse and normalize a search query.
        measure_response_time(query: str, *args, **kwargs) -> float:
            Measure end-to-end response time for a query.
        measure_processing_time(query: str, *args, **kwargs) -> float:
            Measure query preprocessing time.
        measure_database_time(query: str, *args, **kwargs) -> float:
            Measure database operation time.
        measure_ranking_time(query: str, results: list[dict[str, Any]], *args, **kwargs) -> float:
            Measure result ranking time.
        measure_response_time_async(query: str, *args, **kwargs) -> float:
            Async version of response time measurement.
        measure_query_capacity() -> float:
            Calculate the capacity ratio (max query volume / design query volume).
        set_design_query_volume(volume: int) -> None:
            Set the expected peak query volume.
        design_query_volume() -> int:
            Get the current design query volume setting.
        measure_max_query_volume() -> int:
            Determine the maximum query volume before degradation.
        detect_load_degradation() -> bool:
            Identify when the system is approaching capacity limits.
        measure_dependency_resilience() -> float:
            Calculate the overall resilience ratio.
        track_dependency_failure(dependency: str, recovered: bool) -> None:
            Record a dependency failure and whether it was recovered.
        _reset_dependency_tracking() -> None:
            Reset dependency tracking counters.
        get_dependency_resilience(dependency: str) -> float:
            Get resilience metrics for a specific dependency.
        circuit_breaker_status(dependency: str) -> str:
            Get the current circuit breaker status for a dependency.
        measure_error_rate() -> float:
            Calculate the current error rate.
        track_errors(error_details: str) -> None:
            Record occurrence of an error.
        track_operations(operation_details: str) -> None:
            Record a successful or failed operation.
        reset_error_tracking() -> None:
            Reset error and operation counters.
        classify_error(error: Exception) -> str:
            Categorize an error by type and severity.

    Properties:
        results() -> Optional[list[dict[str, Any]]]:
            Get the results of the last search operation.
    """

    def __init__(self, resources: dict[str, Callable] = None, configs: Configs = None) -> None:
        """
        Initialize a new SearchEngine instance.
        
        Args:
            resources (dict[str, Callable], optional): Dictionary of callable functions 
                for search operations. Defaults to None.
            configs (Configs, optional): Configuration settings. Defaults to None.
        """
        self.configs = configs
        self.resources = resources or {}

        # Initialize search components
        self._ranking_algorithm = self.resources['ranking_algorithm']
        self._text_search = self.resources['text_search']
        self._image_search = self.resources['image_search'] 
        self._voice_search = self.resources['voice_search']
        self._exact_match = self.resources['exact_match']
        self._fuzzy_match = self.resources['fuzzy_match']
        self._string_exclusion = self.resources['string_exclusion']
        self._filter_criteria = self.resources['filter_criteria']
        self._multi_field_search = self.resources['multi_field_search']
        self._query_parser = self.resources['query_parser']

        self.logger: logging.Logger = self.resources['logger']

        self._word_piece_tokenizer = self.resources['word_piece_tokenizer'] # Something like nltk.WordPunctTokenizer()

        # Dependencies
        self._db: Database = self.resources.get('db')
        self._llm = None # Natural language to Elasticsearch query conversion, if needed

        self._results: list[dict[str, Any]] = []

        self._max_query_length = configs.get('max_query_length', 1000)  # Default max query length
        self._rolling_window_size = configs.get('rolling_window_size', 1000)  # Default rolling window size for capacity analysis

        # Performance measurement tracking
        self._last_processing_time_in_ms: float = 0.0
        self._last_database_time_in_ms: float = 0.0
        self._last_ranking_time_in_ms: float = 0.0
        self._last_total_time_in_ms: float = 0.0
        
        # Query volume tracking
        self._design_query_volume: int = 100  # Default: 100 QPS
        self._query_count: int = 0
        self._query_start_time: float = time.time()
        self._response_times: list[float] = []
        
        # Error tracking
        self._error_count: int = 0
        self._operation_count: int = 0
        self._error_lock = threading.Lock()

        self._error_history: list[dict] = []
        self._error_types: dict = {}
        self._error_patterns: dict = {}
        self._error_times: list = []

        # Dependency resilience tracking
        self._dependency_failures: dict[str, int] = {}
        self._dependency_recovery: dict[str, int] = {}
        self._circuit_breakers: defaultdict[str, dict] = defaultdict(lambda: {})
        self._dependency_lock = threading.Lock()

        # Operation tracking
        self._operation_history: list[dict] = []
        self._operation_types: dict = {}
        self._operation_times: list = []


    def calculate_duration_ms(self, start_time: float) -> float:
        """Calculate duration in milliseconds."""
        assert isinstance(start_time, float), f"Start time must be a float, got {type(start_time)}"
        assert start_time > 0, f"Start time {start_time} must be positive, got {start_time}"
        end_time = now()
        assert end_time >= start_time, f"End time {end_time} must be greater than or equal to start time {start_time}"
        return (end_time - start_time) * MILLISECOND_SCALAR  # Convert to milliseconds


    async def search(self, query: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform a search operation using the provided query.
        TODO This method is all sorts of fucked up.

        Args:
            query (str): The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: The search results.
        """
        _type_check_str(query)
        _value_check_str(query)

        start_time = now()
        weights: list[float] = [1.0] * len(self.resources.get('fields', []))  # Default weights for multi-field search TODO These are not used at all.
        try:
            # Track this operation
            self.track_operations(f"search: {query}")

            # Parse and process the query
            parsed_query = await self.query_parser(query)

            # Capture processing time
            self._last_processing_time_in_ms = self.calculate_duration_ms(start_time)

            # Execute database operations
            # Here we're simulating different search types based on query content
            # TODO - Implement a more sophisticated query parser that can handle complex queries
            if "image:" in parsed_query:
                results = self.image_search(parsed_query.split("image:")[1].strip(), *args, **kwargs)
            elif "voice:" in parsed_query:
                results = self.voice_search(parsed_query.split("voice:")[1].strip(), *args, **kwargs)
            elif '"' in parsed_query:
                # Extract the phrase inside quotes
                phrase = re.findall(r'"([^"]*)"', parsed_query)
                self.exact_match(phrase[0], *args, **kwargs) if phrase else self.text_search(parsed_query, *args, **kwargs)
            elif "-" in parsed_query:
                # Handle exclusion operator
                terms = parsed_query.split("-", 1)
                results = self.string_exclusion(terms[0].strip(), terms[1].strip(), *args, **kwargs)
            else:
                # Default to text search
                results = self.text_search(parsed_query, *args, **kwargs)

            # Capture database time
            self._last_database_time_in_ms = self.calculate_duration_ms(start_time)

            # Apply ranking algorithm and store results
            self._results = self.ranking_algorithm(parsed_query, results, *args, **kwargs)
            
            # Capture ranking time
            self._last_ranking_time_in_ms = self.calculate_duration_ms(start_time)

            # Capture total time
            self._last_total_time_in_ms = self.calculate_duration_ms(start_time)

            # Store response time for capacity analysis
            self._response_times.append(self._last_total_time_in_ms)
            if len(self._response_times) > self._rolling_window_size:
                self._response_times.pop(0)  # Keep the list from growing too large

            # Update query count for volume tracking
            with self._error_lock:
                self._query_count += 1

            return self._results

        except Exception as e:
            # Track this error
            error_type = self.classify_error(e)
            self.track_errors(f"{error_type}: {e}")
            msg = f"Search operation failed: {e}"

            # Log the error
            self.logger.exception(msg)

            # Re-raise the exception
            raise RuntimeError(msg) from e


    async def text_search(self, query: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform a text-based search operation.

        Args:
            query (str): The text search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results.
        """
        img_desc = kwargs.pop('image_description', None)
        if img_desc is not None:
            query = img_desc

        _type_check_str(query)

        if not query.strip():
            return []

        try:
            results = await self._text_search(query, self._db, *args, **kwargs)
        except Exception as e:
            raise DependencyError(f"Text search failed: {e}") from e

        # Apply ranking if needed
        if kwargs.get("apply_ranking", True):
            return self.ranking_algorithm(query, results, *args, **kwargs)
        return results


    async def image_search(self, image_path: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform an image-based search operation.
        
        Args:
            image_path (str): Path to the image file or image data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results.
        """
        _type_check_str(image_path)
        _value_check_str(image_path)
        try:
            return await self._image_search(image_path, self._db, *args, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")
        except Exception as e:
            raise DependencyError(f"Image search failed: {e}") from e


    async def voice_search(self, audio_path: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform a voice-based search operation.
        
        Args:
            audio_path (str): Path to the audio file or audio data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results.
        """
        _type_check_str(audio_path)
        _value_check_str(audio_path)
        try:
            return await self._voice_search(audio_path, self._db, *args, **kwargs)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Audio file not found: {audio_path}") from e
        except Exception as e:
            raise DependencyError(f"Voice search failed: {e}") from e


    @fallback('text_search')
    async def exact_match(self, phrase: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform an exact phrase matching search.
        
        Args:
            phrase (str): The exact phrase to search for.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results containing the exact phrase.
        """
        return await self._exact_match(phrase, self._db, *args, **kwargs)


    @fallback('text_search')
    async def fuzzy_match(self, term: str, threshold: float = 0.8, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform a fuzzy matching search with configurable threshold.

        Args:
            term (str): The term to search for with fuzzy matching.
            threshold (float, optional): Similarity threshold (0.0-1.0). Defaults to 0.8.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: The search results matching the fuzzy criteria.
        """
        return await self._fuzzy_match(term, threshold, self._db, *args, **kwargs)

    @fallback('text_search')
    async def string_exclusion(self, include_term: str, exclude_term: str, *args, **kwargs) -> list[dict[str, Any]]:
        """
        Perform a search that excludes specific terms.
        
        Args:
            include_term (str): The term to search for.
            exclude_term (str): The term to exclude from results.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The search results containing include_term but not exclude_term.
        """
        return await self._string_exclusion(include_term, exclude_term, self._db, *args, **kwargs)


    @fallback('text_search')
    async def filter_criteria(self, criteria: dict[str, Any], *args, **kwargs) -> list[dict[str, Any]]:
        """
        Apply arbitrary filtering criteria to search results.
        
        Args:
            criteria (dict[str, Any]): Dictionary of field-value pairs to filter by.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The filtered search results.
        """
        return await self._filter_criteria(criteria, self._db, *args, **kwargs)


    def _return_input(self, results, *args, **kwargs):
        """Passthrough function to return input results as-is."""
        return results

    @fallback('_return_input')
    async def ranking_algorithm(self, query: str, results: list[dict[str, Any]], *args, **kwargs) -> list[dict[str, Any]]:
        """
        Sort and rank search results based on relevance.
        
        Args:
            query (str): The original search query.
            results (list[dict[str, Any]]): The unranked search results.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            list[dict[str, Any]]: The ranked search results.
        """
        scored_results = await self._ranking_algorithm(query, results, *args, **kwargs)
        return [result for result, _ in scored_results]

    @fallback('text_search')
    async def multi_field_search(
        self, 
        query: str, 
        fields: list[str], 
        weights: Optional[list[float]] = None, 
        *args, 
        **kwargs
        ) -> Optional[list[dict[str, Any]]]:
        """
        Search across multiple fields with configurable weights.

        Args:
            query (str): The search query.
            fields (list[str]): The fields to search in.
            weights (list[float], optional): The weights for each field. Defaults to None.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: The search results.
        """
        _type_check_str(query)
        _value_check_str(query)

       # Process the query
        parsed_query = self.query_parser(query, *args, **kwargs)

        # Default equal weights if none provided
        if weights is None:
            weights = [1.0] * len(fields)

        # Prepare weights if provided
        weighted_fields = fields
        if weights and len(weights) == len(fields):
            weighted_fields = [f"{field}^{weight}" for field, weight in zip(fields, weights)]

        return await self._multi_field_search(query, weighted_fields, self._db, *args, **kwargs)

    def _split_on_whitespace(self, query: str) -> list[str]:
        """Split a query string into tokens based on whitespace."""
        return " ".join(query.split())

    @fallback('_split_on_whitespace')
    async def query_parser(self, query: str, *args, **kwargs) -> str:
        """
        Parse and normalize a search query.
        # TODO - Implement a more sophisticated query parser that can handle complex queries,

        Args:
            query (str): The raw search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            str: The parsed and normalized query.

        Raises:
            DependencyError: If the query parser fails and cannot recover.
            RuntimeError: If an unexpected error occurs during query parsing.
        """
        _type_check_str(query)
        _value_check_str(query)

        parsed_query: str = await self._query_parser(query, *args, **kwargs)

        # Apply any custom transformations from kwargs
        if kwargs.get('lowercase', True):
            parsed_query = parsed_query.lower()
        return parsed_query


    async def measure_response_time(self, query: str, *args, **kwargs) -> float:
        """
        Measure end-to-end response time for a query.
        
        Args:
            query (str): The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            float: The total response time in milliseconds.
        """
        start_time = now()

        try:
            _ = await self.search(query, *args, **kwargs)
        except Exception as e:
            msg = f"Error during response time measurement: {e}"
            self.logger.exception(msg)
            raise RuntimeError(msg) from e

        return self.calculate_duration_ms(start_time)

    async def measure_processing_time(self, query: str, *args, **kwargs) -> float:
        """
        Measure query preprocessing time.
        
        Args:
            query (str): The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            float: The processing time in milliseconds.
        """
        start_time = now()

        try:
            _ = await self.query_parser(query, *args, **kwargs)
        except Exception as e:
            msg = f"Error during processing time measurement: {e}"
            self.logger.exception(msg)
            raise RuntimeError(msg) from e

        return self.calculate_duration_ms(start_time)

    async def measure_database_time(self, query: str, *args, **kwargs) -> float:
        """Measure database operation time.
        
        Args:
            query (str): The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            float: The database operation time in milliseconds.
        """
        _type_check_str(query)
        _value_check_str(query)

        # First parse the query
        parsed_query = await self.query_parser(query, *args, **kwargs)

        start_time = now()

        try:
            # TODO - Remove simulation of database operations
            # Simulate database operations by executing the appropriate search function
            if "image:" in parsed_query:
                self.image_search(parsed_query.split("image:")[1].strip(), *args, **kwargs)
            elif "voice:" in parsed_query:
                self.voice_search(parsed_query.split("voice:")[1].strip(), *args, **kwargs)
            elif '"' in parsed_query:
                phrase = re.findall(r'"([^"]*)"', parsed_query)
                self.exact_match(phrase[0], *args, **kwargs) if phrase else self.text_search(parsed_query, *args, **kwargs)
            elif "-" in parsed_query:
                terms = parsed_query.split("-", 1)
                self.string_exclusion(terms[0].strip(), terms[1].strip(), *args, **kwargs)
            else:
                self.text_search(parsed_query, *args, **kwargs)
        except Exception as e:
            msg = f"Error during database time measurement: {e}"
            self.logger.exception(msg)
            raise RuntimeError(msg) from e

        return self.calculate_duration_ms(start_time)

    async def measure_ranking_time(self, query: str, results: list[dict[str, Any]], *args, **kwargs) -> float:
        """
        Measure result ranking time.
        
        Args:
            query (str): The search query.
            results (list[dict[str, Any]]): The unranked search results.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            float: The ranking time in milliseconds.
        """
        start_time = now()
        _ = await self.ranking_algorithm(query, results, *args, **kwargs)
        return self.calculate_duration_ms(start_time)

    async def measure_response_time_async(self, query: str, *args, **kwargs) -> float:
        """
        Async version of response time measurement.
        TODO - Implement a proper async search method.
        
        Args:
            query (str): The search query.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
            
        Returns:
            float: The total response time in milliseconds.
        """
        start_time = now()
        _ = await self.search(query, *args, **kwargs)
        return self.calculate_duration_ms(start_time)

    def measure_query_capacity(self) -> float:
        """Calculate the capacity ratio (max query volume / design query volume).
        
        Returns:
            float: The capacity ratio.
        """
        return self.measure_max_query_volume() / self.design_query_volume

    @property
    def design_query_volume(self) -> int:
        """Get the current design query volume setting.
        
        Returns:
            int: The current design query volume in queries per second.
        """
        return self._design_query_volume

    @design_query_volume.setter
    def design_query_volume(self, volume: int) -> None:
        """
        Set the expected peak query volume.
        
        Args:
            volume (int): The expected peak query volume in queries per second.
        
        Raises:
            ValueError: If volume is not positive.
        """
        if not isinstance(volume, int):
            raise TypeError("Design query volume must be an integer")
        if volume <= 0:
            raise ValueError("Design query volume must be positive")
        self._design_query_volume = volume

    @staticmethod
    def _calculate_percentiles(times: list[float], *args) -> tuple[float, ...]:
        """Calculate specified percentiles from a list of times."""
        sorted_times = sorted(times)
        return tuple(sorted_times[int(arg * len(sorted_times))] for arg in args)

    @staticmethod
    def _calculate_capacity_factor(percentiles: tuple[float, ...], cap: float = 3.0) -> tuple[float, ...]:
        """Calculate capacity degradation factor based on percentiles."""
        # Define acceptable thresholds (ms)
        # (Optimal, Acceptable, Poor)
        targets = (100.0, 250.0, 500.0)

        degradation_factors = tuple(target / max(p, 1.0) for p, target in zip(percentiles, targets))

        # Use the most restrictive factor (lowest)
        return min(min(degradation_factors), cap)

    def measure_max_query_volume(self, min_sample_size: int = 31, max_factor_cap: float | int = 3.0) -> int:
        """Determine the maximum query volume before degradation.

        Uses percentile-based analysis of response times to estimate capacity.

        Args:
            min_sample_size (int): Minimum number of samples required for analysis. Defaults to 31.
            max_factor_cap (float, int): Maximum cap for capacity factor. Defaults to 3.0.

        Returns:
            int: Estimated maximum query volume in queries per second.
        """
        factors = (0.5, 0.95, 0.99)  # Percentiles to consider

        assert isinstance(min_sample_size, int), f"Minimum sample size must be an integer, got {type(min_sample_size).__name__}"
        assert min_sample_size >= 1, "Minimum sample size must be non-negative"

        assert isinstance(max_factor_cap, (int, float)), f"Max factor cap must be a number, got {type(max_factor_cap).__name__}"
        assert max_factor_cap > 1.0, f"Max factor cap must be greater than 1.0, got {max_factor_cap}"

        # Calculate current query rate
        time_window = now() - self._query_start_time
        assert time_window > 0, f"Time window must be positive, got {time_window}"

        # Need at least X samples for meaningful analysis
        if len(self._response_times) < min_sample_size:
            return self._design_query_volume

        percentiles  = self._calculate_percentiles(self._response_times, *factors)

        capacity_factor = self._calculate_capacity_factor(*percentiles, cap=max_factor_cap)

        # Apply capacity factor to current performance
        current_qps = self._query_count / time_window

        if current_qps > 0:
            estimated_max = int(current_qps * capacity_factor)
            # Don't estimate below current performance if we're not degraded
            return max(estimated_max, int(current_qps)) if capacity_factor >= 1.0 else estimated_max

        # Fallback if no current load
        return int(self._design_query_volume * capacity_factor)

    def detect_load_degradation(self, most_recent_queries: int = 10, threshold: float = 0.2) -> bool:
        """
        Identify when the system is approaching capacity limits.

        Args:
            most_recent_queries (int): Number of most recent queries to consider for recent average.
            threshold (float): Percentage increase threshold to signal degradation (e.g., 0.2 for 20%).
        
        Returns:
            bool: True if the system is experiencing load degradation, False otherwise.
        """
        assert isinstance(most_recent_queries, int), f"most_recent_queries must be an integer, got {type(most_recent_queries).__name__}"
        assert most_recent_queries > 0, f"most_recent_queries must be positive, got {most_recent_queries}"
        assert isinstance(threshold, (int, float)), f"threshold must be a number, got {type(threshold).__name__}"
        assert 0 < threshold < 1, f"threshold must be between 0 and 1, got {threshold}"

        # If we don't have enough response time data, assume no degradation.
        if len(self._response_times) < most_recent_queries:
            return False

        # Calculate baseline average (excluding recent queries)
        baseline_data = self._response_times[:-most_recent_queries]
        if not baseline_data:
            return False

        # Calculate recent average response time (last 10 queries)
        recent_avg = sum(self._response_times[-most_recent_queries:]) / most_recent_queries

        baseline_avg = sum(baseline_data) / len(baseline_data)

        # Check if recent average is significantly higher than baseline
        return recent_avg > baseline_avg * (1 + threshold)

    def measure_dependency_resilience(self) -> float:
        """
        Calculate the overall resilience ratio.
        
        Returns:
            float: The resilience ratio (recovered failures / total failures).
        """
        with self._dependency_lock:
            try:
                return sum(self._dependency_recovery.values()) / sum(self._dependency_failures.values())
            except ZeroDivisionError:
                return 1.0  # Perfect resilience if no failures

    def track_dependency_failure(self, dependency: str, recovered: bool, failure_threshold: int = 5) -> None:
        """
        Record a dependency failure and whether it was recovered.

        Args:
            dependency (str): The name of the dependency that failed.
            recovered (bool): Whether the failure was recovered.
            failure_threshold (int): Number of failures before opening the circuit breaker.
        """
        with self._dependency_lock:
            # Initialize counters if this is the first failure for this dependency
            if dependency not in self._dependency_failures:
                self._dependency_failures[dependency] = 0
                self._dependency_recovery[dependency] = 0

            # Increment failure count
            self._dependency_failures[dependency] += 1

            # Increment recovery count if recovered
            if recovered:
                self._dependency_recovery[dependency] += 1

            # Update circuit breaker state
            if dependency not in self._circuit_breakers:
                dependency_dict = defaultdict(int)
                dependency_dict['state'] = DependencyState.CLOSED.value
                self._circuit_breakers[dependency] = dependency_dict

            circuit = self._circuit_breakers[dependency]
            assert circuit['state'] in {state.value for state in DependencyState}, f"Invalid circuit state: {circuit['state']}"

            match circuit['state']:
                case DependencyState.CLOSED.value: 
                    # Increment failure count
                    circuit['failure_count'] += 1
                    circuit['last_failure_time'] = time.time()

                    # Open circuit if failure threshold reached
                    if circuit['failure_count'] >= failure_threshold:  
                        circuit['state'] = DependencyState.OPEN.value
                        self.logger.warning(f"Circuit breaker opened for dependency: {dependency}")
    
                case DependencyState.OPEN.value:
                    if recovered:
                        # Reset circuit if recovery successful
                        circuit['state'] = DependencyState.CLOSED.value
                        circuit['failure_count'] = 0
                        self.logger.info(f"Circuit breaker closed for dependency: {dependency} after successful recovery")
                    else:
                        # Back to open state if recovery failed
                        circuit['state'] = DependencyState.OPEN.value
                        circuit['last_failure_time'] = time.time()
                        self.logger.warning(f"Circuit breaker reopened for dependency: {dependency} after failed recovery attempt")


    def _reset_dependency_tracking(self) -> None:
        """Reset dependency tracking counters."""
        with self._dependency_lock:
            for trackers in [self._dependency_failures, self._dependency_recovery, self._circuit_breakers]:
                trackers.clear()


    def get_dependency_resilience(self, dependency: str) -> float:
        """
        Get resilience metrics for a specific dependency.
        
        Args:
            dependency (str): The name of the dependency.
            
        Returns:
            float: The resilience ratio for the specified dependency.
        """
        with self._dependency_lock:
            if dependency not in self._dependency_failures:
                return 1.0  # Perfect resilience if no failures

            num_fails = self._dependency_failures[dependency]
            assert num_fails >= 0, f"Failure count should never be negative, got {num_fails}"
            if num_fails == 0:
                return 1.0

            recoveries = self._dependency_recovery[dependency]
            assert recoveries >= 0, f"Recovery count should never be negative, got {recoveries}"
            assert recoveries <= num_fails, f"Recovery count {recoveries} should never exceed failure count {num_fails}"

            return recoveries / num_fails


    def circuit_breaker_status(self, dependency: str, recovery_attempt_interval: int = 30) -> str:
        """
        Get the current circuit breaker status for a dependency.
        
        Args:
            dependency (str): The name of the dependency.
            recovery_attempt_interval (int): Time in seconds to wait before attempting recovery from open state.
            
        Returns:
            str: The circuit breaker status ('closed', 'open', or 'half-open').
        """
        with self._dependency_lock:
            if dependency not in self._circuit_breakers:
                return DependencyState.CLOSED.value

            circuit = self._circuit_breakers[dependency]

            # Check if it's time to try recovery for open circuit
            match circuit['state']:
                case DependencyState.CLOSED.value:

                    # Wait a bit before trying recovery
                    recovery_timestamp = time.time()
                    if recovery_timestamp - circuit['last_failure_time'] > recovery_attempt_interval:
                        circuit['state'] = DependencyState.HALF_OPEN.value
                        circuit['recovery_timestamp'] = recovery_timestamp
                        self.logger.info(f"Circuit breaker half-opened for dependency: {dependency}")

            return circuit['state']

    def measure_error_rate(self) -> float:
        """
        Calculate the current error rate.
        
        Returns:
            float: The error rate (errors / operations).
        """
        with self._error_lock:
            assert self._operation_count >= 0, f"Operation count should never be negative, got {self._operation_count}"
            if self._operation_count == 0:
                return 0.0

            return self._error_count / self._operation_count

    def track_errors(self, error_details: str) -> None:
        """
        Record occurrence of an error with detailed tracking and analysis.
        
        Args:
            error_details (str): Details about the error.
        """
        with self._error_lock:
            self._error_count += 1

            # Parse error details
            parts = error_details.split(': ', 1)
            type_ = parts[0] if len(parts) > 0 else 'unknown'
            msg = parts[1] if len(parts) > 1 else error_details

            # Create detailed error record
            record = {
                'timestamp': time.time(),
                'type': type_,
                'message': msg,
                'error_id': self._error_count,
                'operation_id': self._operation_count,
                'severity': self._determine_severity(type_, msg)
            }

            # Store error record
            self._error_history.append(record)

            # Maintain rolling window (keep last 1000 errors)
            if len(self._error_history) > self._rolling_window_size:
                self._error_history.pop(0)

            # Track error types count
            if type_ not in self._error_types:
                self._error_types[type_] = 0
            self._error_types[type_] += 1

            # Track error patterns for analysis
            pattern = self._extract_error_pattern(msg)
            if pattern not in self._error_patterns:
                self._error_patterns[pattern] = 0
            self._error_patterns[pattern] += 1

            # Track error timing
            self._error_times.append(time.time())
            if len(self._error_times) > self._rolling_window_size:
                self._error_times.pop(0)

            # Update operation history to mark failure
            if self._operation_history:
                # Mark the most recent operation as failed
                self._operation_history[-1]['success'] = False
                self._operation_history[-1]['error_details'] = error_details

            # Log critical errors immediately
            match record['severity']:
                case ErrorLevel.CRITICAL.value:
                    self.logger.error(f"Critical error tracked: {error_details}")
                    # Stop the program for critical errors
                    raise AssertionError(f"Critical error occurred: {error_details}")

    def _determine_severity(self, error_type: str, error_msg: str) -> str:
        """Determine error severity level."""
        critical_patterns = ['database_error', 'network_error', 'timeout_error']
        high_patterns = ['search_error', 'dependency_error']

        if error_type in critical_patterns:
            return ErrorLevel.CRITICAL.value
        elif error_type in high_patterns:
            return ErrorLevel.HIGH.value
        elif 'warning' in error_msg.lower():
            return ErrorLevel.LOW.value
        else:
            return ErrorLevel.MEDIUM.value
    
    def _extract_error_pattern(self, error_msg: str, max_length: int = 100) -> str:
        """Extract common patterns from error messages for grouping."""
        assert isinstance(error_msg, str), f"Error message must be a string, got {type(error_msg).__name__}"
        assert isinstance(max_length, int), f"Max length must be an integer, got {type(max_length).__name__}"
        assert max_length > 0, f"Max length must be positive, got {max_length}"

        pattern_dict = {
            "N": r'\d+',
            "PATH": r'/[^\s]+',
            "UUID": r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        }
        for key, regex in pattern_dict.items():
            error_msg = re.sub(regex, key, error_msg)
        return error_msg[:max_length]  # Limit pattern length

    
    def get_error_statistics(self, top_k: int = 5) -> dict[str, Any]:
        """
        Get comprehensive error statistics.
        
        Returns:
            dict[str, Any]: A dictionary containing error statistics.
            Keys are the following:
                - total_errors: Total number of errors recorded.
                - error_rate: Current error rate (errors / operations).
                - recent_errors_count: Number of errors in the last hour.
                - error_types: Breakdown of errors by type.
                - common_patterns : Most common error message patterns.
                - severity_breakdown (ErrorLevel): Breakdown of errors by severity level.
                - error_frequency (float): Errors per minute over the last hour.
        
        """
        assert isinstance(top_k, int), f"top_k must be an integer, got {type(top_k).__name__}"
        assert top_k > 0, f"top_k must be positive, got {top_k}"

        with self._error_lock:

            right_now = time.time()
            recent_errors = [e for e in self._error_history if right_now - e['timestamp'] < HOUR_IN_SECONDS]  # Last hour

            output_dict = {
                'total_errors': self._error_count,
                'error_rate': self.measure_error_rate(),
                'recent_errors_count': len(recent_errors),
                'error_types': dict(self._error_types),
                'common_patterns': dict(sorted(self._error_patterns.items(), key=lambda x: x[1], reverse=True)[:top_k]),
                'severity_breakdown': self._get_severity_breakdown(),
                'error_frequency': self._calculate_error_frequency()
            }
            return output_dict
    
    def _get_severity_breakdown(self) -> dict[str, int]:
        """Get breakdown of errors by severity."""
        breakdown = defaultdict(int)
        for error in self._error_history:
            breakdown[error['severity']] += 1
        return breakdown

    def _calculate_error_frequency(self) -> float:
        """Calculate errors per minute over the last hour."""
        right_now = now()
        recent_errors = [t for t in self._error_times if right_now - t < HOUR_IN_SECONDS]

        if len(self._error_times) < 2 or len(recent_errors) < 2:
            return 0.0

        time_span_minutes = (max(recent_errors) - min(recent_errors)) / MINUTE_IN_SECONDS
        return len(recent_errors) / max(time_span_minutes, 1.0)


    def track_operations(self, operation_details: str) -> None:
        """
        Record a successful or failed operation with detailed tracking.
        
        Args:
            operation_details (str): Details about the operation.
        """
        
        assert isinstance(operation_details, str), f"Operation details must be a string, got {type(operation_details).__name__}"
        op_details = operation_details.strip()
        assert op_details, "Operation details must not be an empty string."

        with self._error_lock:
            self._operation_count += 1

            # Parse operation details
            parts = op_details.split(': ', 1)

            # Record operation with timestamp
            record = {
                'timestamp': time.time(),
                'type': parts[0] if len(parts) > 0 else 'unknown',
                'query': parts[1] if len(parts) > 1 else '',
                'operation_id': self._operation_count,
                'success': True  # Assume success unless error is tracked separately
            }
            
            # Store operation record
            self._operation_history.append(record)
            
            # Maintain rolling window
            if len(self._operation_history) > self._rolling_window_size:
                self._operation_history.pop(0)

            # Track operation types count
            if record['type'] not in self._operation_types:
                self._operation_types[record['type']] = 0
            self._operation_types[record['type']] += 1

            # Track operation timing
            self._operation_times.append(time.time())
            if len(self._operation_times) > self._rolling_window_size:
                self._operation_times.pop(0)

    def reset_error_tracking(self) -> None:
        """
        Reset error and operation counters.
        """
        with self._error_lock:
            self._error_count = 0
            self._operation_count = 0

    def classify_error(self, error: Exception) -> str:
        """
        Categorize an error by type and severity.
        
        Args:
            error (Exception): The error to classify.
            
        Returns:
            str: The error classification.
        """
        match type(error).__name__:
            case "DatabaseError" | "OperationalError" | "IntegrityError":
                return "database_error"
            case "ConnectionError" | "TimeoutError":
                return "network_error"
            case "SearchError" | "QueryError":
                return "search_error"
            case "TimeoutError":
                return "timeout_error"
            case "ValueError" | "TypeError":
                return "input_error"
            case _:
                # Check error message content if class name doesn't match
                error_msg = str(error).lower()
                if "database" in error_msg:
                    return "database_error"
                elif "network" in error_msg:
                    return "network_error"
                elif "search" in error_msg:
                    return "search_error"
                elif "timeout" in error_msg:
                    return "timeout_error"
                elif "input" in error_msg:
                    return "input_error"
                else:
                    return "unknown_error"

    @property
    def results(self) -> list[dict[str, Any]]:
        """
        Get the results of the last search operation.

        Returns:
            list[dict[str, Any]]: The results of the last search.
        """
        return self._results

