import concurrent.futures
import itertools

import tqdm

def run_in_thread_pool(func, inputs, *, max_concurrency=5):
    """
    Execute a function across multiple inputs in parallel using a thread pool.
    
    This function processes a collection of inputs by applying the provided function
    to each input using a thread pool for concurrent execution. It yields results as
    they complete rather than waiting for all to finish, which is useful for long-running
    operations.
    
    Args:
        func (callable): A function that takes a single input argument. This function
            will be called once for each item in the inputs collection.
        inputs (iterable): A collection of input values to process. Each element will
            be passed individually to the function.
        max_concurrency (int, optional): Maximum number of concurrent threads to use.
            Defaults to 5.
            
    Yields:
        tuple: (input, output) pairs as the function calls complete, where:
            - input: The original input value passed to the function
            - output: The return value from calling func(input)
            
    Note:
        - Results are yielded in the order they complete, not in the order of inputs
        - Progress is displayed using tqdm
        - For CPU-bound operations, consider using run_in_process_pool instead
        
    Example:
        >>> def square(x):
        ...     return x * x
        >>> for input_val, result in run_in_thread_pool(square, [1, 2, 3, 4, 5]):
        ...     print(f"{input_val} squared is {result}")
    
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