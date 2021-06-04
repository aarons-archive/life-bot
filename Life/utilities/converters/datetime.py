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

from typing import Union

import dateparser.search
import pendulum
from discord.ext import commands

import config
from utilities import context, exceptions


class DatetimeConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> dict[str, Union[str, dict[str, pendulum.DateTime]]]:

        if not (searches := dateparser.search.search_dates(argument, languages=['en'], settings=config.DATEPARSER_SETTINGS)):
            raise exceptions.ArgumentError('I was unable to find a time and/or date within your query, try to be more explicit or put the time/date first.')

        data = {'argument': argument, 'found': {str(phrase): pendulum.instance(datetime, tz='UTC') for phrase, datetime in searches}}

        if not data['found']:
            raise exceptions.ArgumentError('I was able to find a time and/or date within your query, however it seems to be in the past.')

        return data
