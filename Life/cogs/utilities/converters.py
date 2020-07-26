"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC

import discord
import yarl
from discord.ext import commands

from cogs.utilities import exceptions


class TagName(commands.clean_content):

    async def convert(self, ctx: commands.Context, argument: str):

        argument = await super().convert(ctx, argument)
        argument = discord.utils.escape_markdown(argument)
        argument = argument.strip()

        if not argument:
            raise commands.BadArgument

        if argument.split(' ')[0] in ctx.bot.get_command('tag').all_commands:
            raise exceptions.ArgumentError('Your tag name can not start with a tag subcommand.')
        if '`' in argument:
            raise exceptions.ArgumentError('Your tag name can not contain backtick characters.')
        if len(argument) > 50:
            raise exceptions.ArgumentError('Your tag name can not be more than 50 characters.')

        return argument


class ImageConverter(commands.Converter, ABC):

    async def convert(self, ctx: commands.Context, argument: str):

        url = None

        try:
            member = await ctx.bot.member_converter.convert(ctx, str(argument))
        except commands.BadArgument:
            pass
        else:
            url = ctx.bot.utils.member_avatar(member=member)

        if url is None:
            check = yarl.URL(argument)
            if check.scheme and check.host:
                url = argument

        return url
