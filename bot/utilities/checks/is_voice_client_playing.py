# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from core import colours, emojis
from utilities import context, exceptions


T = TypeVar("T")


def is_voice_client_playing() -> Callable[[T], T]:

    async def predicate(ctx: context.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="No tracks are currently playing."
            )

        return True

    return commands.check(predicate)
