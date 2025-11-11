# backend/utils/async_helpers.py

"""
Async utility functions for the framework.
"""

import asyncio
from typing import Callable, TypeVar, Any, Coroutine
from functools import wraps

T = TypeVar("T")


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run an async coroutine in a synchronous context.

    Args:
        coro: Coroutine to run

    Returns:
        Result of the coroutine

    Example:
        ```python
        result = run_async(some_async_function())
        ```
    """
    try:
        asyncio.get_running_loop()
        # Already in an async context
        raise RuntimeError(
            "Cannot use run_async() from within an async context. "
            "Use 'await' instead."
        )
    except RuntimeError:
        # No running loop, create a new one
        return asyncio.run(coro)


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch

    Example:
        ```python
        @async_retry(max_attempts=5, delay=2.0)
        async def fetch_data():
            # May fail with transient errors
            return await api_call()
        ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        raise
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but just in case
            raise last_exception

        return wrapper

    return decorator


async def gather_with_concurrency(
    n: int, *tasks: Coroutine
) -> list:
    """
    Run coroutines with a maximum concurrency limit.

    Args:
        n: Maximum number of concurrent tasks
        *tasks: Coroutines to run

    Returns:
        List of results in the same order as tasks

    Example:
        ```python
        results = await gather_with_concurrency(
            5,  # Max 5 concurrent requests
            fetch(url1),
            fetch(url2),
            # ... 100 more tasks
        )
        ```
    """
    semaphore = asyncio.Semaphore(n)

    async def bounded_task(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(bounded_task(task) for task in tasks))
