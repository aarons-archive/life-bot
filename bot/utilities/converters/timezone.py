# Future
from __future__ import annotations

# Packages
import pendulum
import rapidfuzz
from discord.ext import commands
from pendulum.tz.timezone import Timezone

# My stuff
from core import colours
from utilities import custom, exceptions


class TimezoneConverter(commands.Converter[Timezone]):

    async def convert(self, ctx: custom.Context, argument: str) -> Timezone:

        if argument not in pendulum.timezones:
            msg = "\n".join(f"- {match}" for match, _, _ in rapidfuzz.process.extract(query=argument, choices=pendulum.timezones))
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That was not a recognised timezone. Maybe you meant one of these?\n{msg}"
            )

        return pendulum.timezone(argument)
