# run_in_process_pool.py: last updated 12:47 AM on April 05, 2025

**File Path:** `utils/run_in_process_pool.py`

## Table of Contents

### Functions

- [`run_in_process_pool`](#run_in_process_pool)

## Functions

## `run_in_process_pool`

```python
def run_in_process_pool(func, inputs)
```

Calls the function ``func`` on the values ``inputs``.

``func`` should be a function that takes a single input, which is the
individual values in the iterable ``inputs``.

Generates (input, output) tuples as the calls to ``func`` complete.

See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
of how this function works.

**Parameters:**

- `func` (`Callable`): The function to call on each input.
inputs: An iterable of inputs to pass to the function.
max_concurrency: The maximum number of concurrent workers. If None, defaults to all CPU cores minus one.
