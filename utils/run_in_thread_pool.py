import concurrent.futures
import itertools

import tqdm

def run_in_thread_pool(func, inputs, *, max_concurrency=5):
    """
    Calls the function ``func`` on the values ``inputs``.

    ``func`` should be a function that takes a single input, which is the
    individual values in the iterable ``inputs``.

    Generates (input, output) tuples as the calls to ``func`` complete.

    See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
    of how this function works.

    """
    # Make sure we get a consistent iterator throughout, rather than
    # getting the first element repeatedly.
    func_inputs = iter(inputs)

    with tqdm.tqdm(total=len(inputs)) as pbar:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(func, input): input
                for input in itertools.islice(func_inputs, max_concurrency)
            }

            while futures:
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )

                for fut in done:
                    original_input = futures.pop(fut)
                    pbar.update(1)
                    yield original_input, fut.result()

                for input in itertools.islice(func_inputs, len(done)):
                    fut = executor.submit(func, input)
                    futures[fut] = input