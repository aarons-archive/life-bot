# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from core import colours
from utilities import custom, exceptions


T = TypeVar("T")


def is_queue_not_empty() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or ctx.voice_client.queue.is_empty():
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="The queue is empty."
            )

        return True

    return commands.check(predicate)


def is_queue_history_not_empty() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.queue._queue_history:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="The queue history is empty."
            )

        return True

    return commands.check(predicate)
