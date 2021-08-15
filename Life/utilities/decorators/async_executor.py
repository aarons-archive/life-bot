import asyncio
import functools
from typing import Any, Callable


def async_executor(function: Callable[..., Any]) -> Callable[..., Any]:

    @functools.wraps(function)
    async def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(function, *args, **kwargs))

    return wrapper
