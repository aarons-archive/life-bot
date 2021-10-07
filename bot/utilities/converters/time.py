# Future
from __future__ import annotations

# Standard Library
import re

# Packages
from discord.ext import commands

# My stuff
from core import colours
from utilities import custom, exceptions


COLON_FORMAT_REGEX = re.compile(r"""
^
    (?:
        (?:
            (?P<hours>[0-1]?[0-9]|2[0-3]):
        )?
        (?P<minutes>[0-5]?[0-9]):
    )?
    (?P<seconds>[0-5]?[0-9])
$
""", flags=re.VERBOSE)

HUMAN_FORMAT_REGEX = re.compile(r"""
^
    (?: (?P<hours>[0-1]?[0-9]|2[0-3]) \s? (?:h|hour|hours)              (?:\s?|\s?and\s?) )?
    (?: (?P<minutes>[0-5]?[0-9])      \s? (?:m|min|mins|minute|minutes) (?:\s?|\s?and\s?) )?
    (?: (?P<seconds>[0-5]?[0-9])      \s? (?:s|sec|secs|second|seconds)                   )?
$
""", flags=re.VERBOSE)


class TimeConverter(commands.Converter):

    async def convert(self, ctx: custom.Context, argument: str) -> int:

        if (match := COLON_FORMAT_REGEX.match(argument)) or (match := HUMAN_FORMAT_REGEX.match(argument)):

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
                    description="That time format was not recognized."
                )

        return total
