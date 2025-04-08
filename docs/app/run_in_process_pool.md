# run_in_process_pool.py: last updated 02:01 AM on April 08, 2025

**File Path:** `/home/kylerose1946/american_law_search/app/utils/common/run_in_process_pool.py`

## Table of Contents

### Functions

- [`run_in_process_pool`](#run_in_process_pool)

## Functions

## `run_in_process_pool`

```python
def run_in_process_pool(func, inputs)
```

Execute a function across multiple inputs in parallel using separate processes.

This function processes a collection of inputs by applying the provided function
to each input using a process pool for parallel execution. It yields results as
they complete rather than waiting for all to finish. This is ideal for CPU-bound
operations that benefit from true parallel execution.

**Parameters:**

- `func (Callable)` (`Any`): A function that takes a single input argument. This function
will be called once for each item in the inputs collection.
inputs (Container): A collection of input values to process. Each element will
be passed individually to the function.
max_concurrency (Optional[int], optional): Maximum number of concurrent processes.
If None, defaults to (CPU cores - 1). Defaults to None.

**Returns:**

- `Generator[(None, None, tuple[(Any, Optional[Any])])]`: A generator that yields
        (input, output) pairs as the function calls complete, where:
        - input: The original input value passed to the function
        - output: The return value from calling func(input)

**Examples:**

```python
>>> def complex_calculation(x):
    ...     return x ** 3
    >>> for input_val, result in run_in_process_pool(complex_calculation, range(10)):
    ...     print(f"{input_val}³ = {result}")

See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
of how this function works.
```
