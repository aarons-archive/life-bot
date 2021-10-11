# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from core import colours
from utilities import custom, exceptions
from utilities.checks.is_author_connected import is_author_connected


T = TypeVar("T")


def has_voice_client(try_join: bool) -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> Literal[True]:

        if not ctx.voice_client or ctx.voice_client.is_connected() is False:

            if try_join:
                await is_author_connected(same_channel=False).predicate(ctx)  # type: ignore
                await ctx.invoke(ctx.bot.get_command("join"))
            else:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    description="I am not connected to any voice channels."
                )

        return True

    return commands.check(predicate)
