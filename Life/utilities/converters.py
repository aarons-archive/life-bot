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
from typing import Union

import dateparser.search
import discord
import pendulum
import pendulum.exceptions
import rapidfuzz.process
import yarl
from discord.ext import commands
from pendulum.tz.timezone import Timezone

import config
from utilities import context, exceptions


class ChannelEmojiConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel]) -> str:

        if isinstance(channel, discord.VoiceChannel):
            emoji = 'voice_locked' if channel.overwrites_for(channel.guild.default_role).connect is False else 'voice'

        elif isinstance(channel, discord.TextChannel):
            if channel.is_news():
                emoji = 'news_locked' if channel.overwrites_for(channel.guild.default_role).read_messages is False else 'news'
            elif channel.is_nsfw():
                emoji = 'text_nsfw'
            else:
                emoji = 'text_locked' if channel.overwrites_for(channel.guild.default_role).read_messages is False else 'text'

        else:
            emoji = 'unknown'

        return config.CHANNEL_EMOJIS[emoji]


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

        if argument not in pendulum.timezones:
            msg = '\n'.join(f'`{index + 1}.` {match[0]}' for index, match in enumerate(
                    rapidfuzz.process.extract(query=argument, choices=pendulum.timezones, processor=lambda s: s)
            ))
            raise exceptions.ArgumentError(f'That was not a recognised timezone. Maybe you meant one of these?\n{msg}')

        return pendulum.timezone(argument)


class TagNameConverter(commands.clean_content, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        argument = discord.utils.escape_markdown(await super().convert(ctx, argument)).strip()

        if not argument:
            raise commands.BadArgument

        if argument.split(' ')[0] in ctx.bot.get_command('tag').all_commands:
            raise exceptions.ArgumentError('Your tag name can not start with a tag subcommand.')
        if '`' in argument:
            raise exceptions.ArgumentError('Your tag name can not contain backtick characters.')
        if len(argument) < 3 or len(argument) > 50:
            raise exceptions.ArgumentError('Your tag name must be between 3 and 50 characters long.')

        return argument


class TagContentConverter(commands.clean_content, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        argument = (await super().convert(ctx, argument)).strip()

        if not argument:
            raise commands.BadArgument

        if len(argument) > 1024:
            raise exceptions.ArgumentError('Your tag content can not be more than 1024 characters long.')

        return argument



class DatetimeConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> dict:

        searches = dateparser.search.search_dates(argument, languages=['en'], settings=config.DATEPARSER_SETTINGS)
        if not searches:
            raise exceptions.ArgumentError('I was unable to find a time and/or date within your query, try to be more explicit or put the time/date first.')

        data = {'argument': argument, 'found': {}}

        for datetime_phrase, datetime in searches:
            datetime = pendulum.instance(dt=datetime, tz='UTC')
            data['found'][datetime_phrase] = datetime

        if not data['found']:
            raise exceptions.ArgumentError('I was able to find a time and/or date within your query, however it seems to be in the past.')

        return data



#


class ImageConverter(commands.Converter, ABC):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        url = None

        try:
            member = await commands.MemberConverter().convert(ctx=ctx, argument=str(argument))
        except commands.BadArgument:
            pass
        else:
            url = str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png'))

        if url is None:
            try:
                user = await UserConverter().convert(ctx=ctx, argument=str(argument))
            except commands.BadArgument:
                pass
            else:
                url = str(user.avatar_url_as(format='gif' if user.is_avatar_animated() is True else 'png'))

        if url is None:
            check = yarl.URL(argument)
            if check.scheme and check.host:
                url = argument

        if url is None:
            raise commands.ConversionError

        return url


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
