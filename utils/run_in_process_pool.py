import concurrent.futures
import itertools
from typing import Callable, Container, Optional


import psutil
import tqdm


def run_in_process_pool(
        func: Callable, 
        inputs: Container, *, 
        max_concurrency: Optional[int] = None,
        ):
    """
    Calls the function ``func`` on the values ``inputs``.

    ``func`` should be a function that takes a single input, which is the
    individual values in the iterable ``inputs``.

    Generates (input, output) tuples as the calls to ``func`` complete.

    See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
    of how this function works.
    """
    # Default to using all CPU cores but one.
    if max_concurrency is None:
        max_workers = max_concurrency = psutil.cpu_count(logical=False) - 1

    # Make sure we get a consistent iterator throughout, rather than
    # getting the first element repeatedly.
    func_inputs = iter(inputs)

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