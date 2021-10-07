# Future
from __future__ import annotations

# Standard Library
from typing import Callable, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import custom


T = TypeVar("T")


def is_track_requester() -> Callable[[T], T]:

    async def predicate(ctx: custom.Context) -> bool:
        return getattr(getattr(getattr(ctx.voice_client, "current", None), "requester", None), "id", None) == ctx.author.id

    return commands.check(predicate)
