import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar


T = TypeVar("T")
P = ParamSpec("P")


def async_executor(function: Callable[P, T]) -> Callable[P, Coroutine[Any, Any, T]]:

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Coroutine[Any, Any, T]:
        return asyncio.to_thread(function, *args, **kwargs)

    return wrapper
