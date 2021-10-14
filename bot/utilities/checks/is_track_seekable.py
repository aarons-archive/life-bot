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


def is_track_seekable() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not (ctx.voice_client.current and not ctx.voice_client.current.is_seekable()):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="The current track is not seekable."
            )

        return True

    return commands.check(predicate)
