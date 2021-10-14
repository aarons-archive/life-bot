# Future
from __future__ import annotations

# Packages
import dateparser.search
from discord.ext import commands

# My stuff
from core import colours, values
from utilities import custom, exceptions, objects


class PastPhrasedDatetimeConverter(commands.Converter[objects.PastPhrasedDatetimeSearch]):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.PastPhrasedDatetimeSearch:

        datetimes = dateparser.search.search_dates(argument, languages=["en"], settings=values.DATE_PARSER_SETTINGS)

        if not datetimes:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="I couldn't find a time or date in that input."
            )

        return objects.PastPhrasedDatetimeSearch(argument, datetimes=datetimes)


class FuturePhrasedDatetimeConverter(commands.Converter[objects.FuturePhrasedDatetimeSearch]):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.FuturePhrasedDatetimeSearch:

        settings = values.DATE_PARSER_SETTINGS.copy()
        settings["PREFER_DATES_FROM"] = "future"

        datetimes = dateparser.search.search_dates(argument, languages=["en"], settings=settings)

        if not datetimes:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="I couldn't find a time or date in that input."
            )

        return objects.FuturePhrasedDatetimeSearch(argument, datetimes=datetimes)
