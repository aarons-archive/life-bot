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


def is_author_connected() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        author_channel = ctx.author.voice and ctx.author.voice.channel
        voice_client_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if voice_client_channel != author_channel:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"You must be connected to {voice_client_channel.mention} to use this command.",
            )

        return True

    return commands.check(predicate)
