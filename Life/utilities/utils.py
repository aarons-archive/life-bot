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

from __future__ import annotations

import codecs
import colorsys
import datetime as dt
import logging
import os
import pathlib
from typing import Literal, Optional, TYPE_CHECKING, Union

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


__log__ = logging.getLogger('utilities.utils')


def convert_datetime(datetime: Union[dt.datetime, pendulum.DateTime]) -> pendulum.DateTime:

    if type(datetime) is dt.datetime and datetime.tzinfo == dt.timezone.utc:
        datetime = datetime.replace(tzinfo=None)

    return pendulum.instance(datetime, tz='UTC')


def format_datetime(datetime: Union[dt.datetime, pendulum.DateTime], *, seconds: bool = False) -> str:

    datetime = convert_datetime(datetime)
    return datetime.format(f'dddd MMMM Do YYYY [at] hh:mm{":ss" if seconds else ""} A zzZZ')


def format_date(datetime: Union[dt.datetime, pendulum.DateTime]) -> str:

    datetime = convert_datetime(datetime)
    return datetime.format('dddd MMMM Do YYYY')


def format_difference(datetime: Union[dt.datetime, pendulum.DateTime], *, suppress: list[str] = None) -> str:

    if suppress is None:
        suppress = ['seconds']

    datetime = convert_datetime(datetime)
    return humanize.precisedelta(pendulum.now(tz=datetime.timezone).diff(datetime), format='%0.0f', suppress=suppress)


def format_seconds(seconds: int, *, friendly: bool = False) -> str:

    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

    if friendly is True:
        return f'{f"{days}d " if not days == 0 else ""}{f"{hours}h " if not hours == 0 or not days == 0 else ""}{minutes}m {seconds}s'

    return f'{f"{days:02d}:" if not days == 0 else ""}{f"{hours:02d}:" if not hours == 0 or not days == 0 else ""}{minutes:02d}:{seconds:02d}'


def channel_emoji(channel: Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel], *, guild: discord.Guild, member: discord.Member) -> str:

    overwrites = channel.permissions_for(member)

    if isinstance(channel, discord.StageChannel):
        emoji = 'STAGE' if overwrites.connect else 'STAGE_LOCKED'
    elif isinstance(channel, discord.VoiceChannel):
        emoji = 'VOICE' if overwrites.connect else 'VOICE_LOCKED'
    elif channel == guild.rules_channel:
        emoji = 'RULES'
    else:
        if channel.is_news():
            emoji = 'ANNOUNCEMENT' if overwrites.read_messages else 'ANNOUNCEMENT_LOCKED'
        elif channel.is_nsfw():
            emoji = 'TEXT_NSFW'
        else:
            emoji = 'TEXT' if overwrites.read_messages else 'TEXT_LOCKED'

    return config.CHANNELS[emoji]


def badge_emojis(person: Union[discord.User, discord.Member]) -> str:

    badges = [badge for badge_name, badge in config.BADGES.items() if dict(person.public_flags)[badge_name] is True]

    if dict(person.public_flags)['verified_bot'] is False and person.bot:
        badges.append(config.BOT)
    if isinstance(person, discord.Member) and person.premium_since:
        badges.append(config.BOOSTER)

    if person.avatar.is_animated():
        badges.append(config.NITRO)

    elif isinstance(person, discord.Member) and ((activity_list := [activity for activity in person.activities if isinstance(activity, discord.CustomActivity)]) is not None):
        if activity_list[0].emoji and activity_list[0].emoji.is_custom_emoji():
            badges.append(config.NITRO)

    return ' '.join(badges) if badges else 'N/A'


def activities(member: discord.Member) -> str:   # sourcery no-metrics

    if not member.activities:
        return 'N/A'

    message = []

    for activity in member.activities:

        if isinstance(activity, discord.Activity):

            if activity.type is discord.ActivityType.playing:
                message.append(f'• Playing **{activity.name}** {f" | **{activity.details}**" if activity.details else ""}{f" | **{activity.state}**" if activity.state else ""}')

            elif activity.type is discord.ActivityType.watching:
                message.append(f'• Watching **{activity.name}**')

            elif activity.type is discord.ActivityType.competing:
                message.append(f'• Competing in **{activity.name}**')

        elif isinstance(activity, discord.Spotify):

            message.append(f''' \
            • Listening to **[{activity.title}](https://open.spotify.com/track/{activity.track_id})** by **{", ".join(activity.artists)}** \
            {f" from the album **{activity.album}**" if activity.album and activity.album != activity.title else ""} \
            ''')

        elif isinstance(activity, discord.Game):
            message.append(f'• Playing **{activity.name}**')

        elif isinstance(activity, discord.Streaming):
            message.append(f'• Streaming **[{activity.name}]({activity.url})** on **{activity.platform}**')

        elif isinstance(activity, discord.CustomActivity):
            message.append(f'• {f"{activity.emoji} " if activity.emoji else ""}{f"{activity.name}" if activity.name else ""}')

    return '\n'.join(message)


def avatar(person: Union[discord.User, discord.Member], *, format: Literal['webp', 'jpeg', 'jpg', 'png', 'gif'] = None, size: int = 1024) -> Optional[str]:
    return str(person.avatar.replace(format=format or ('gif' if person.avatar.is_animated() else 'png'), size=size)) if person.avatar else None


def icon(guild: discord.Guild, *, format: Literal['webp', 'jpeg', 'jpg', 'png', 'gif'] = None, size: int = 1024) -> Optional[str]:
    return str(guild.icon.replace(format=format or ('gif' if guild.icon.is_animated() else 'png'), size=size)) if guild.icon else None


def banner(guild: discord.Guild, *, format: Literal['webp', 'jpeg', 'jpg', 'png', 'gif'] = None, size: int = 1024) -> Optional[str]:
    return str(guild.banner.replace(format=format or ('gif' if guild.banner.is_animated() else 'png'), size=size)) if guild.banner else None


def splash(guild: discord.Guild, *, format: Literal['webp', 'jpeg', 'jpg', 'png', 'gif'] = None, size: int = 1024) -> Optional[str]:
    return str(guild.splash.replace(format=format or ('gif' if guild.splash.is_animated() else 'png'), size=size)) if guild.splash else None


def format_command(command: commands.Command) -> str:
    return f'{config.PREFIX}{command.qualified_name}'


def voice_region(obj: Union[discord.VoiceChannel, discord.StageChannel, discord.Guild]) -> str:

    if not (region := obj.rtc_region if isinstance(obj, (discord.VoiceChannel, discord.StageChannel)) else obj.region):
        return 'Automatic'

    if region is discord.VoiceRegion.hongkong:
        region_name = 'Hong Kong'
    elif region is discord.VoiceRegion.southafrica:
        region_name = 'South Africa'
    else:
        region_name = obj.name.title().replace('Vip', 'VIP').replace('_', '-').replace('Us-', 'US-')

    return region_name


def name(person: Union[discord.Member, discord.User], *, guild: discord.Guild = None) -> str:

    if guild and isinstance(person, discord.User):
        member = guild.get_member(person.id)
        return member.nick or member.name if isinstance(member, discord.Member) else getattr(person, 'name', 'Unknown')

    return person.nick or person.name if isinstance(person, discord.Member) else getattr(person, 'name', 'Unknown')


#


async def upload_image(bot: Life, file: discord.File, file_format: str = 'png') -> str:

    data = aiohttp.FormData()
    data.add_field('file', file.fp, filename=f'file.{file_format.lower()}')

    async with bot.session.post(config.CDN_UPLOAD_URL, headers=config.CDN_HEADERS, data=data) as response:

        if response.status == 413:
            raise exceptions.GeneralError('The image produced was too large to upload.')

        post = await response.json()

    return f'https://media.mrrandom.xyz/{post.get("filename")}'


async def safe_content(mystbin_client: mystbin.Client, content: str, *, syntax: str = 'txt', max_characters: int = 1024) -> str:

    if len(content) <= max_characters:
        return content

    try:
        paste = await mystbin_client.post(content, syntax=syntax)
        return paste.url
    except mystbin.APIError:
        return content[:max_characters]


#


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


def darken_colour(r, g, b, factor: float = 0.1) -> tuple[float, float, float]:

    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    r, g, b = colorsys.hls_to_rgb(h, max(min(l * (1 - factor), 1.0), 0.0), s)
    return int(r * 255), int(g * 255), int(b * 255)


def lighten_colour(r, g, b, factor: float = 0.1) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    r, g, b = colorsys.hls_to_rgb(h, max(min(l * (1 + factor), 1.0), 0.0), s)
    return int(r * 255), int(g * 255), int(b * 255)
