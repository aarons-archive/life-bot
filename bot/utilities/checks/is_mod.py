# Future
from __future__ import annotations

# Standard Library
from typing import Callable, Literal, TypeVar

# Packages
from discord.ext import commands

# My stuff
from utilities import checks, context


T = TypeVar("T")


def is_mod() -> Callable[[T], T]:

    async def predicate(ctx: context.Context) -> Literal[True]:

        unwrapped = [
            wrapped.predicate for wrapped in  # type: ignore
            [
                commands.is_owner(),
                checks.is_guild_owner(),
                checks.has_any_permissions(
                    manage_channels=True, manage_roles=True, manage_guild=True, kick_members=True, ban_members=True, administrator=True
                )
            ]
        ]
        errors = []

        for func in unwrapped:
            try:
                value = await func(ctx)
            except commands.CheckFailure as e:
                errors.append(e)
            else:
                if value:
                    return True

        raise commands.CheckAnyFailure(unwrapped, errors)  # type: ignore

    return commands.check(predicate)
