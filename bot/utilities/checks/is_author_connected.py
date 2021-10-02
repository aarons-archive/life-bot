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


def is_author_connected(same_channel: bool) -> Callable[[T], T]:

    async def predicate(ctx: context.Context) -> Literal[True]:

        author_channel = ctx.author.voice and ctx.author.voice.channel
        voice_client_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if same_channel is True and voice_client_channel is not None and author_channel != voice_client_channel:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"You must be connected to {voice_client_channel.mention} to use this command.",
            )

        if not author_channel:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="You must be connected to a voice channel to use this command.",
            )

        return True

    return commands.check(predicate)
