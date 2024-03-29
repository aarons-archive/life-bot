# Future
from __future__ import annotations

# Standard Library
from typing import Callable, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import custom


T = TypeVar("T")


def is_owner() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> bool:

        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner('You do not own this bot.')

        return True

    return commands.check(predicate)
