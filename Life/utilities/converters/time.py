import re

from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


COLON_REGEX = re.compile(r"^(?:(?:(?P<hours>[01]?\d|2[0-3]):)?(?P<minutes>[0-5]?\d):)?(?P<seconds>[0-5]?\d)$")
HUMAN_REGEX = re.compile(r"^(?:(?P<hours>[01]?\d|2[0-3])\s?(h|hour|hours)\s?)?(?:(?P<minutes>[0-5]?\d)\s?(m|min|mins|minutes)\s?)?(?:(?P<seconds>[0-5]?\d)\s?(s|sec|secs|seconds))?$")


class TimeConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> int:

        if (match := COLON_REGEX.match(argument)) or (match := HUMAN_REGEX.match(argument)):

            total = 0

            if hours := match.group("hours"):
                total += int(hours) * 60 * 60
            if minutes := match.group("minutes"):
                total += int(minutes) * 60
            if seconds := match.group("seconds"):
                total += int(seconds)

        else:

            try:
                total = int(argument)
            except ValueError:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="That time format was not recognized."
                )

        return total
