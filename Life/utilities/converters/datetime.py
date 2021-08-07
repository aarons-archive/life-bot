from typing import Any

import dateparser.search
import pendulum
from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


SETTINGS = {
    "DATE_ORDER":               "DMY",

    "TIMEZONE":                 "UTC",
    "RETURN_AS_TIMEZONE_AWARE": False,

    "PREFER_DAY_OF_MONTH":      "current",
    "PREFER_DATES_FROM":        "future",

    "PARSERS":                  ["relative-time", "absolute-time", "timestamp"]
}


class DatetimeConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> tuple[str, dict[str, pendulum.DateTime]]:

        searches: Any = dateparser.search.search_dates(argument, languages=["en"], settings=SETTINGS)
        if not searches:
            raise exceptions.EmbedError(colour=colours.RED, description=f"{emojis.CROSS}  I couldn't find a time or date in that input.")

        return argument, {phrase: pendulum.instance(datetime, tz="UTC") for phrase, datetime in searches}
