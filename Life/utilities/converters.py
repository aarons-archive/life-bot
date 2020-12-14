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
#

from abc import ABC

import dateparser.search
import discord
import pendulum
import pendulum.exceptions
import rapidfuzz.process
import yarl
from discord.ext import commands
from pendulum.tz.timezone import Timezone

from utilities import context, exceptions


class UserConverter(commands.UserConverter):

    async def convert(self, ctx: context.Context, argument: str) -> discord.User:

        user = None
        try:
            user = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass

        if not user:
            try:
                user = await ctx.bot.fetch_user(argument)
            except (discord.NotFound, discord.HTTPException):
                raise commands.UserNotFound(argument=argument)

        return user


class TimezoneConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> Timezone:

        timezones = [timezone for timezone in pendulum.timezones]

        if argument not in timezones:
            matches = rapidfuzz.process.extract(query=argument, choices=pendulum.timezones, limit=5)
            extra_message = '\n'.join(f'`{index + 1}.` {match[0]}' for index, match in enumerate(matches))
            raise exceptions.ArgumentError(f'That was not a recognised timezone. Maybe you meant one of these?\n{extra_message}')

        return pendulum.timezone(argument)


class ChannelEmojiConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, channel: discord.abc.GuildChannel) -> str:

        if isinstance(channel, discord.VoiceChannel):
            emoji = 'voice'
            if channel.overwrites_for(channel.guild.default_role).connect is False:
                emoji = 'voice_locked'

        else:
            if channel.is_news():
                emoji = 'news'
                if channel.overwrites_for(channel.guild.default_role).read_messages is False:
                    emoji = 'news_locked'
            else:
                emoji = 'text'
                if channel.is_nsfw():
                    emoji = 'text_nsfw'
                elif channel.overwrites_for(channel.guild.default_role).read_messages is False:
                    emoji = 'text_locked'

        return ctx.bot.utils.channel_emojis[emoji]


class ImageConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        url = None

        try:
            user = await UserConverter().convert(ctx=ctx, argument=str(argument))
        except commands.BadArgument:
            pass
        else:
            url = str(user.avatar_url_as(format='gif' if user.is_avatar_animated() is True else 'png'))

        if url is None:
            try:
                member = await commands.MemberConverter().convert(ctx=ctx, argument=str(argument))
            except commands.BadArgument:
                pass
            else:
                url = str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png'))

        if url is None:
            check = yarl.URL(argument)
            if check.scheme and check.host:
                url = argument

        if url is None:
            url = str(ctx.author.avatar_url_as(format='gif' if ctx.author.is_avatar_animated() is True else 'png'))

        return url


class DatetimeConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> dict:

        searches = dateparser.search.search_dates(argument, languages=['en'], settings=ctx.bot.dateparser_settings)
        if not searches:
            raise exceptions.ArgumentError('I was unable to find a time and/or date within your query, try to be more explicit or put the time/date first.')

        data = {'argument': argument, 'found': {}}

        for datetime_phrase, datetime in searches:
            datetime = pendulum.instance(dt=datetime, tz='UTC')
            data['found'][datetime_phrase] = datetime

        if not data['found']:
            raise exceptions.ArgumentError('I was able to find a time and/or date within your query, however it seems to be in the past.')

        return data


class TagConverter(commands.clean_content, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        argument = await super().convert(ctx, argument)
        argument = discord.utils.escape_markdown(argument)
        argument = argument.strip()

        if not argument:
            raise commands.BadArgument

        if argument.split(' ')[0] in ctx.bot.get_command('tag').all_commands:
            raise exceptions.ArgumentError('Your tag name can not start with a tag subcommand.')
        if '`' in argument:
            raise exceptions.ArgumentError('Your tag name can not contain backtick characters.')
        if len(argument) < 3 or len(argument) > 50:
            raise exceptions.ArgumentError('Your tag name must be between 3 and 50 characters long.')

        return argument


class PrefixConverter(commands.clean_content, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        argument = await super().convert(ctx, argument)
        argument = discord.utils.escape_markdown(argument)

        if not argument:
            raise commands.BadArgument

        if '`' in argument:
            raise exceptions.ArgumentError('Your prefix can not contain backtick characters.')
        if len(argument) > 15:
            raise exceptions.ArgumentError('Your prefix can not be more than 15 characters.')

        return argument
