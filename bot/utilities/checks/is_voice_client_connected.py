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


def is_voice_client_connected() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="I am not connected to any voice channels."
            )

        return True

    return commands.check(predicate)
