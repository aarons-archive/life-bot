# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import dateparser.search
import pendulum
from discord.ext import commands

# My stuff
from core import colours, emojis
from utilities import custom, exceptions


FUTURE_SETTINGS = {
    "DATE_ORDER":               "DMY",
    "TIMEZONE":                 "UTC",
    "RETURN_AS_TIMEZONE_AWARE": False,
    "PREFER_DAY_OF_MONTH":      "current",
    "PREFER_DATES_FROM":        "future",
    "PARSERS":                  ["relative-time", "absolute-time", "timestamp"],
}

PAST_SETTINGS = {
    "DATE_ORDER":               "DMY",
    "TIMEZONE":                 "UTC",
    "RETURN_AS_TIMEZONE_AWARE": False,
    "PREFER_DAY_OF_MONTH":      "current",
    "PREFER_DATES_FROM":        "future",
    "PARSERS":                  ["relative-time", "absolute-time", "timestamp"],
}


class FutureDatetimeConverter(commands.Converter):

    async def convert(self, ctx: custom.Context, argument: str) -> tuple[str, dict[str, pendulum.DateTime]]:

        searches: Any = dateparser.search.search_dates(argument, languages=["en"], settings=FUTURE_SETTINGS)
        if not searches:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="I couldn't find a time or date in that input."
            )

        return argument, {phrase: pendulum.instance(datetime, tz="UTC") for phrase, datetime in searches}


class PastDatetimeConverter(commands.Converter):

    async def convert(self, ctx: custom.Context, argument: str) -> tuple[str, dict[str, pendulum.DateTime]]:

        searches: Any = dateparser.search.search_dates(argument, languages=["en"], settings=PAST_SETTINGS)
        if not searches:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="I couldn't find a time or date in that input."
            )

        return argument, {phrase: pendulum.instance(datetime, tz="UTC") for phrase, datetime in searches}
