import asyncio
import functools
import typing

def AsyncExecutor(sync_function: typing.Callable):
    """A decorator that wraps a sync function in an executor, changing it into an async function.
    This allows processing functions to be wrapped and used immediately as an async function.
    """

    @functools.wraps(sync_function)
    async def sync_wrapper(*args, **kwargs):
        """
        Asynchronous function that wraps a sync function with an executor.
        """

        loop = asyncio.get_event_loop()
        internal_function = functools.partial(sync_function, *args, **kwargs)
        return await loop.run_in_executor(None, internal_function)

    return sync_wrapper
