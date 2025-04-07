import asyncio
import concurrent.futures
import itertools
from typing import Any, AsyncGenerator, Callable, Container, Coroutine, Generator, Optional


import psutil
import tqdm


def run_in_process_pool(
        func: Callable, 
        inputs: Container, *, 
        max_concurrency: Optional[int] = None,
        ) -> Generator[None, None, tuple[Any, Optional[Any]]]:
    """
    Execute a function across multiple inputs in parallel using separate processes.
    
    This function processes a collection of inputs by applying the provided function
    to each input using a process pool for parallel execution. It yields results as
    they complete rather than waiting for all to finish. This is ideal for CPU-bound
    operations that benefit from true parallel execution.
    
    Args:
        func (Callable): A function that takes a single input argument. This function
            will be called once for each item in the inputs collection.
        inputs (Container): A collection of input values to process. Each element will
            be passed individually to the function.
        max_concurrency (Optional[int], optional): Maximum number of concurrent processes.
            If None, defaults to (CPU cores - 1). Defaults to None.
            
    Returns:
        Generator[None, None, tuple[Any, Optional[Any]]]: A generator that yields
            (input, output) pairs as the function calls complete, where:
            - input: The original input value passed to the function
            - output: The return value from calling func(input)
            
    Note:
        - Results are yielded in the order they complete, not in the order of inputs
        - Progress is displayed using tqdm
        - For I/O-bound operations, consider using run_in_thread_pool instead
        - This function properly cleans up resources even if exceptions occur
        - Multiprocessing has overhead, so this is best for compute-intensive tasks
    
    Example:
        >>> def complex_calculation(x):
        ...     return x ** 3
        >>> for input_val, result in run_in_process_pool(complex_calculation, range(10)):
        ...     print(f"{input_val}³ = {result}")
    
    See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
    of how this function works.
    """

    # Default to using all CPU cores but one.
    if max_concurrency is None:
        max_workers = max_concurrency = psutil.cpu_count(logical=False) - 1

    # Make sure we get a consistent iterator throughout, rather than
    # getting the first element repeatedly.
    func_inputs = iter(inputs)

    try:
        with tqdm.tqdm(total=len(inputs)) as pbar:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:

                # Submit the initial batch of futures.
                futures = {
                    executor.submit(func, input): input # For islice, see: https://www.geeksforgeeks.org/python-itertools-islice/
                    for input in itertools.islice(func_inputs, max_concurrency)
                }

                while futures:
                    done, _ = concurrent.futures.wait(
                        futures, return_when=concurrent.futures.FIRST_COMPLETED
                    )

                    # Yield the results of the completed futures.
                    for fut in done:
                        original_input = futures.pop(fut)
                        pbar.update(1)
                        yield original_input, fut.result()

                    # Schedule the next set of futures.
                    for input in itertools.islice(func_inputs, len(done)):
                        fut = executor.submit(func, input)
                        futures[fut] = input
    finally:
        # Force cleanup of any remaining futures
        futures.clear()
        # Make sure to garbage collect any remaining futures
        import gc
        gc.collect()


async def async_run_in_process_pool(
        func: Callable | Coroutine, 
        inputs: Container, *, 
        max_concurrency: Optional[int] = None
        ) -> AsyncGenerator[None, tuple[Any, Optional[Any]]]:
    """
    Asynchronously execute a function across multiple inputs using separate processes.
    
    This is the asynchronous version of run_in_process_pool that integrates with asyncio.
    It processes a collection of inputs by applying the provided function to each input
    using a process pool, but allows other asynchronous operations to continue while
    waiting for results by not blocking the event loop.
    
    Args:
        func (Callable | Coroutine): A function or coroutine that takes a single input argument.
            This function will be called once for each item in the inputs collection.
        inputs (Container): A collection of input values to process. Each element will
            be passed individually to the function.
        max_concurrency (Optional[int], optional): Maximum number of concurrent processes.
            If None, defaults to (CPU cores - 1). Defaults to None.
            
    Returns:
        AsyncGenerator[None, tuple[Any, Optional[Any]]]: An async generator that yields
            (input, output) pairs as the function calls complete, where:
            - input: The original input value passed to the function
            - output: The return value from calling func(input)
            
    Note:
        - Results are yielded in the order they complete, not in the order of inputs
        - Progress is displayed using tqdm
        - This function integrates with the asyncio event loop
        - The event loop remains responsive to other tasks while processing
        - Proper resource cleanup occurs even if exceptions are raised
        - Use 'async for' to iterate over the results
    
    Example:
        >>> async def process_data():
        ...     async def complex_calculation(x):
        ...         return x ** 3
        ...     async for input_val, result in async_run_in_process_pool(complex_calculation, range(10)):
        ...         print(f"{input_val}³ = {result}")
    """
    # Default to using all CPU cores but one.
    if max_concurrency is None:
        max_workers = max_concurrency = psutil.cpu_count(logical=False) - 1

    # Make sure we get a consistent iterator throughout
    func_inputs = iter(inputs)
    print("inputs: ", inputs)

    try:
        with tqdm.tqdm(total=len(inputs)) as pbar:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit the initial batch of futures
                futures = {
                    asyncio.wrap_future(
                        executor.submit(func, input), 
                        loop=asyncio.get_event_loop() # Separate event loop for each process.
                    ): input 
                    for input in itertools.islice(func_inputs, max_concurrency)
                }

                # Process futures as they complete
                while futures:
                    # Wait for the first future to complete
                    done, _ = await asyncio.wait(
                        futures.keys(), return_when=asyncio.FIRST_COMPLETED
                    )

                    # Process completed futures
                    for fut in done:
                        #print(f"result: {fut}")
                        original_input = futures.pop(fut)
                        pbar.update(1)
                        output = fut.result() if fut is not None else None
                        yield original_input, output

                    # Schedule the next set of futures
                    for input in itertools.islice(func_inputs, len(done)):
                        async_future = asyncio.wrap_future(
                            executor.submit(func, input), 
                            loop=asyncio.get_event_loop()
                        )
                        futures[async_future] = input
    finally:
        # Force cleanup of any remaining futures
        futures.clear()
        # Make sure to garbage collect any remaining futures
        import gc
        gc.collect()