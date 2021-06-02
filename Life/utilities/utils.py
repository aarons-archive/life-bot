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

from __future__ import annotations

import codecs
import colorsys
import datetime as dt
import logging
import os
import pathlib
from typing import TYPE_CHECKING, Union

import aiohttp
import discord
import humanize
import mystbin
import pendulum
from discord.ext import commands

import config
from utilities import exceptions


if TYPE_CHECKING:
    from bot import Life

__log__ = logging.getLogger(__name__)


async def safe_text(text: str, mystbin_client: mystbin.Client, max_characters: int = 1024, syntax: str = 'python') -> str:

    if len(text) <= max_characters:
        return text

    try:
        return await mystbin_client.post(text, syntax=syntax)
    except mystbin.APIError as error:
        __log__.warning(f'[ERRORS] Error while uploading error traceback to mystbin | Code: {error.status_code} | Message: {error.message}')
        return f'{text[:max_characters]}'  # Not the best solution.


def convert_datetime(datetime: Union[dt.datetime, pendulum.datetime]) -> pendulum.datetime:
    return pendulum.instance(datetime, tz='UTC') if isinstance(datetime, dt.datetime) else datetime


def format_datetime(datetime: Union[dt.datetime, pendulum.datetime], *, seconds: bool = False) -> str:
    datetime = convert_datetime(datetime)
    return datetime.format(f'dddd MMMM Do YYYY [at] hh:mm{":ss" if seconds else ""} A zz{"ZZ" if datetime.timezone.name != "UTC" else ""}')


def format_date(datetime: Union[dt.datetime, pendulum.datetime]) -> str:
    return convert_datetime(datetime).format('dddd MMMM Do YYYY')


def format_difference(datetime: Union[dt.datetime, pendulum.datetime], *, suppress=None) -> str:

    if suppress is None:
        suppress = ['seconds']

    return humanize.precisedelta(pendulum.now(tz='UTC').diff(convert_datetime(datetime)), format='%0.0f', suppress=suppress)


def format_seconds(seconds: int, *, friendly: bool = False) -> str:

    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

    if friendly is True:
        return f'{f"{days}d " if not days == 0 else ""}{f"{hours}h " if not hours == 0 or not days == 0 else ""}{minutes}m {seconds}s'

    return f'{f"{days:02d}:" if not days == 0 else ""}{f"{hours:02d}:" if not hours == 0 or not days == 0 else ""}{minutes:02d}:{seconds:02d}'


def line_count() -> tuple[int, int, int, int]:

    files, functions, lines, classes = 0, 0, 0, 0
    is_docstring = False

    for dirpath, _, filenames in os.walk('.'):

        for filename in filenames:
            if not filename.endswith('.py'):
                continue
            files += 1

            # noinspection PyArgumentEqualDefault
            with codecs.open('./' + str(pathlib.PurePath(dirpath, filename)), 'r', 'utf-8') as filelines:
                filelines = [line.strip() for line in filelines]
                for line in filelines:

                    if len(line) == 0:
                        continue

                    if line.startswith('"""'):
                        is_docstring = not is_docstring
                    if is_docstring:
                        continue

                    if line.startswith('#'):
                        continue
                    if line.startswith(('def', 'async def')):
                        functions += 1
                    if line.startswith('class'):
                        classes += 1
                    lines += 1

    return files, functions, lines, classes


def badges(bot: Life, person: Union[discord.User, discord.Member]) -> str:

    badges_list = [badge for badge_name, badge in config.BADGE_EMOJIS.items() if dict(person.public_flags)[badge_name] is True]
    if dict(person.public_flags)['verified_bot'] is False and person.bot:
        badges_list.append('<:bot:738979752244674674>')

    if any(getattr(guild.get_member(person.id), 'premium_since', None) for guild in bot.guilds):
        badges_list.append('<:booster_level_4:738961099310760036>')

    if person.is_avatar_animated() or any(getattr(guild.get_member(person.id), 'premium_since', None) for guild in bot.guilds):
        badges_list.append('<:nitro:738961134958149662>')

    elif member := discord.utils.get(bot.get_all_members(), id=person.id):  # skipcq: PTC-W0048
        if activity := discord.utils.get(member.activities, type=discord.ActivityType.custom):
            if activity.emoji and activity.emoji.is_custom_emoji():
                badges_list.append('<:nitro:738961134958149662>')

    return ' '.join(badges_list) if badges_list else 'N/A'


def avatar(person: Union[discord.User, discord.Member], img_format: str = None) -> str:
    return str(person.avatar_url_as(format=img_format or 'gif' if person.is_avatar_animated() else 'png'))


def icon(guild: discord.Guild, img_format: str = None) -> str:
    return str(guild.icon_url_as(format=img_format or 'gif' if guild.is_icon_animated() else 'png'))


def activities(person: discord.Member) -> str:  # sourcery no-metrics

    if not person.activities:
        return 'N/A'

    message = '\n'
    for activity in person.activities:

        if activity.type == discord.ActivityType.custom:
            message += '• '
            if activity.emoji:
                message += f'{activity.emoji} '
            if activity.name:
                message += f'{activity.name}'
            message += '\n'

        elif activity.type == discord.ActivityType.playing:

            message += f'• Playing **{activity.name}** '
            if not isinstance(activity, discord.Game):
                if activity.details:
                    message += f'**| {activity.details}** '
                if activity.state:
                    message += f'**| {activity.state}** '
                message += '\n'

        elif activity.type == discord.ActivityType.streaming:
            message += f'• Streaming **[{activity.name}]({activity.url})** on **{activity.platform}**\n'

        elif activity.type == discord.ActivityType.watching:
            message += f'• Watching **{activity.name}**\n'

        elif activity.type == discord.ActivityType.listening:

            if isinstance(activity, discord.Spotify):
                url = f'https://open.spotify.com/track/{activity.track_id}'
                message += f'• Listening to **[{activity.title}]({url})** by **{", ".join(activity.artists)}** '
                if activity.album and activity.album != activity.title:
                    message += f'from the album **{activity.album}** '
                message += '\n'
            else:
                message += f'• Listening to **{activity.name}**\n'

    return message


def channel_emoji(channel: Union[discord.TextChannel, discord.VoiceChannel]) -> str:

    overwrites = channel.overwrites_for(channel.guild.default_role)

    if isinstance(channel, discord.VoiceChannel):
        emoji = 'voice' if overwrites.connect else 'voice_locked'
    else:
        if channel.is_news():
            emoji = 'news' if overwrites.read_messages else 'news_locked'
        elif channel.is_nsfw():
            emoji = 'text_nsfw'
        else:
            emoji = 'text' if overwrites.read_messages else 'text_locked'

    return config.CHANNEL_EMOJIS[emoji]


def darken_colour(r, g, b, factor: float = 0.1) -> tuple[float, float, float]:

    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    r, g, b = colorsys.hls_to_rgb(h, max(min(l * (1 - factor), 1.0), 0.0), s)
    return int(r * 255), int(g * 255), int(b * 255)


def lighten_colour(r, g, b, factor: float = 0.1) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    r, g, b = colorsys.hls_to_rgb(h, max(min(l * (1 + factor), 1.0), 0.0), s)
    return int(r * 255), int(g * 255), int(b * 255)


def format_command(command: commands.Command) -> str:
    return f'{config.PREFIX}{command.qualified_name}'


def voice_region(x: Union[discord.VoiceChannel, discord.StageChannel, discord.Guild]) -> str:

    x = x.rtc_region if isinstance(x, (discord.VoiceChannel, discord.StageChannel)) else x.region
    if not x:
        return 'Automatic'

    region = x.name.title().replace('Vip', 'VIP').replace('_', '-').replace('Us-', 'US-')
    if x == discord.VoiceRegion.hongkong:
        region = 'Hong Kong'
    if x == discord.VoiceRegion.southafrica:
        region = 'South Africa'

    return region


def name(person: Union[discord.Member, discord.User], *, guild: discord.Guild = None) -> str:

    if guild and isinstance(person, discord.User):
        member = guild.get_member(person.id)
        return member.nick or member.name if isinstance(member, discord.Member) else getattr(person, 'name', 'Unknown')

    return person.nick or person.name if isinstance(person, discord.Member) else getattr(person, 'name', 'Unknown')


async def upload_image(bot: Life, file: discord.File, file_format: str = 'png') -> str:

    data = aiohttp.FormData()
    data.add_field('file', file.fp, filename=f'file.{file_format.lower()}')

    async with bot.session.post(config.CDN_UPLOAD_URL, headers=config.CDN_HEADERS, data=data) as response:

        if response.status == 413:
            raise exceptions.GeneralError('The image produced was too large to upload.')

        post = await response.json()

    return f'https://media.mrrandom.xyz/{post.get("filename")}'
