import asyncio
from typing import Any, Callable, Coroutine, Optional


from tqdm import asyncio as tqdm_asyncio


async def limiter(task, limit: asyncio.Semaphore = None):
    """
    Rate limit a coroutine task using a semaphore.
    
    This function wraps an awaitable task with a semaphore to control concurrency.
    It ensures that only a limited number of tasks can run simultaneously.
    
    Args:
        task (Awaitable): The coroutine task to be rate-limited
        limit (asyncio.Semaphore, optional): The semaphore to use for rate limiting.
            If an integer is provided, a new semaphore will be created with that value.
            
    Returns:
        Any: The result of the awaited task
        
    Raises:
        ValueError: If limit is neither a Semaphore nor an integer
    """
    if not isinstance(limit, asyncio.Semaphore):
        if isinstance(limit, int):
            limit = asyncio.Semaphore(limit)
        else:
            raise ValueError(f"The limit must be an instance of asyncio.Semaphore or an integer, not {type(limit)}")
    async with limit:
        return await task


async def run_in_parallel_with_concurrency_limiter(
        func: Callable | Coroutine = None,
        input_list: list[Any] = None,
        concurrency_limit: int = 2,
        **kwargs: dict,
    ) -> Optional[Any]:
    """
    Runs the given function in parallel for each input, with a concurrency limit.

    Args:
        func (Callable | Coroutine): The function or coroutine to be executed in parallel.
        input_list (list[Any]): A list of input values to be processed.
        concurrency_limit (int): A semaphore to limit concurrent executions. Defaults to 2.
        **kwargs (dict): Additional keyword arguments to be passed to the function.

    Returns:
        Optional[Any]:: This function doesn't return a specific value. 
            However, it may yield results

    Raises:
        ValueError: If the required arguments are not provided.

    Note:
        - The function uses a semaphore to limit concurrency.
        - Progress is displayed using tqdm.
        - Each function call receives its input value and any additional kwargs.
    """
    tasks = [
        func(inp, **kwargs) for inp in input_list
    ]

    limited_tasks = [
        limiter(task, limit=asyncio.Semaphore(concurrency_limit)) for task in tasks
    ]

    for future in tqdm_asyncio.tqdm.as_completed(limited_tasks):
        await future
