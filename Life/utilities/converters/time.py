#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.

import re

from discord.ext import commands

from utilities import context, exceptions


COLON_REGEX = re.compile(r'^(?:(?:(?P<hours>[01]?\d|2[0-3]):)?(?P<minutes>[0-5]?\d):)?(?P<seconds>[0-5]?\d)$')
HUMAN_REGEX = re.compile(r'^(?:(?P<hours>[01]?\d|2[0-3])\s?(h|hour|hours)\s?)?(?:(?P<minutes>[0-5]?\d)\s?(m|min|mins|minutes)\s?)?(?:(?P<seconds>[0-5]?\d)\s?(s|sec|secs|seconds))?$')


class TimeConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> int:

        if (match := COLON_REGEX.match(argument)) or (match := HUMAN_REGEX.match(argument)):

            total = 0

            if hours := match.group('hours'):
                total += int(hours) * 60 * 60
            if minutes := match.group('minutes'):
                total += int(minutes) * 60
            if seconds := match.group('seconds'):
                total += int(seconds)

        else:

            try:
                total = int(argument)
            except ValueError:
                raise exceptions.ArgumentError('Time format was not recognized.')

        return total
