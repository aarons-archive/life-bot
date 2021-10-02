# Future
from __future__ import annotations

# Standard Library
from typing import Callable, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import context


T = TypeVar('T')


def is_guild_owner() -> Callable[[T], T]:

    def predicate(ctx: context.Context) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)
