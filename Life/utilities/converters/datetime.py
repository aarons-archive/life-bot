"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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

    "PARSERS":                  ["absolute-time", "relative-time", "timestamp"]
}


class DatetimeConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> tuple[str, dict[str, pendulum.DateTime]]:

        if not (searches := dateparser.search.search_dates(argument, languages=["en"], settings=SETTINGS)):
            raise exceptions.EmbedError(colour=colours.RED, description=f"{emojis.CROSS}  I couldn't find a time or date in that input.")

        return argument, {phrase: pendulum.instance(datetime, tz="UTC") for phrase, datetime in searches}
