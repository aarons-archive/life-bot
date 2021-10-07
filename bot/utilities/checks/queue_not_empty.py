# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from core import colours, emojis
from utilities import custom, exceptions


T = TypeVar("T")


def queue_not_empty() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or ctx.voice_client.queue.is_empty():
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The queue is empty."
            )

        return True

    return commands.check(predicate)
