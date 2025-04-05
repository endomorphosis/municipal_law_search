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
    Calls the function ``func`` on the values ``inputs``.

    ``func`` should be a function that takes a single input, which is the
    individual values in the iterable ``inputs``.

    Generates (input, output) tuples as the calls to ``func`` complete.

    See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
    of how this function works.

    Args:
        func: The function to call on each input.
        inputs: An iterable of inputs to pass to the function.
        max_concurrency: The maximum number of concurrent workers. If None, defaults to all CPU cores minus one.
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
    Asynchronous version of run_in_process_pool using an event loop.

    Calls the function ``func`` on the values ``inputs`` within a ProcessPoolExecutor,
    but uses asyncio to handle the futures without blocking the event loop.

    ``func`` should be a function that takes a single input, which is the
    individual values in the iterable ``inputs``.

    Asynchronously yields (input, output) tuples as the calls to ``func`` complete.

    Args:
        func: The function to call on each input.
        inputs: An iterable of inputs to pass to the function.
        max_concurrency: The maximum number of concurrent workers. If None, defaults to all CPU cores minus one.
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
                        print(f"result: {fut}")
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