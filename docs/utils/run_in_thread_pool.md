# run_in_thread_pool.py: last updated 03:25 PM on March 31, 2025

**File Path:** `utils/run_in_thread_pool.py`

## Table of Contents

### Functions

- [`run_in_thread_pool`](#run_in_thread_pool)

## Functions

## `run_in_thread_pool`

```python
def run_in_thread_pool(func, inputs)
```

Calls the function ``func`` on the values ``inputs``.

``func`` should be a function that takes a single input, which is the
individual values in the iterable ``inputs``.

Generates (input, output) tuples as the calls to ``func`` complete.

See https://alexwlchan.net/2019/10/adventures-with-concurrent-futures/ for an explanation
of how this function works.
