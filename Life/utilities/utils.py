from __future__ import annotations

import colorsys
import datetime as dt
import io
import logging
from typing import Any, Literal, Optional

import aiohttp
import discord
import humanize
import mystbin
import pendulum
from discord.ext import commands

from core import colours, config, emojis, values
from utilities import exceptions


__log__: logging.Logger = logging.getLogger('utilities.utils')


def convert_datetime(datetime: dt.datetime | pendulum.DateTime) -> pendulum.DateTime:
    datetime.replace(microsecond=0)

    if type(datetime) is dt.datetime and datetime.tzinfo == dt.timezone.utc:
        datetime = datetime.replace(tzinfo=None)

    return pendulum.instance(datetime, tz='UTC')


def format_datetime(datetime: dt.datetime | pendulum.DateTime, *, seconds: bool = False) -> str:
    return convert_datetime(datetime).format(f'dddd MMMM Do YYYY [at] hh:mm{":ss" if seconds else ""} A')


def format_date(date: pendulum.Date) -> str:
    return date.format('dddd MMMM Do YYYY')


def format_time(time: pendulum.Time) -> str:
    return time.format(f'hh:mm:ss')


def format_difference(datetime: dt.datetime | pendulum.DateTime, *, suppress: tuple[str] = ("seconds",)) -> str:
    datetime = convert_datetime(datetime)

    now = pendulum.now(tz=datetime.timezone)
    now.replace(microsecond=0)

    return humanize.precisedelta(now.diff(datetime), format='%0.0f', suppress=suppress)


def format_seconds(seconds: float, *, friendly: bool = False) -> str:
    seconds = round(seconds)

    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

    if friendly is True:
        return f'{f"{days}d " if not days == 0 else ""}{f"{hours}h " if not hours == 0 or not days == 0 else ""}{minutes}m {seconds}s'

    return f'{f"{days:02d}:" if not days == 0 else ""}{f"{hours:02d}:" if not hours == 0 or not days == 0 else ""}{minutes:02d}:{seconds:02d}'


def channel_emoji(channel: discord.TextChannel | discord.VoiceChannel | discord.StageChannel, *, guild: discord.Guild, member: discord.Member) -> str:
    overwrites = channel.permissions_for(member)

    if isinstance(channel, discord.StageChannel):
        emoji_name = 'STAGE' if overwrites.connect else 'STAGE_LOCKED'
    elif isinstance(channel, discord.VoiceChannel):
        emoji_name = 'VOICE' if overwrites.connect else 'VOICE_LOCKED'
    elif channel == guild.rules_channel:
        emoji_name = 'RULES'
    elif channel.is_news():
        emoji_name = 'ANNOUNCEMENT' if overwrites.read_messages else 'ANNOUNCEMENT_LOCKED'
    elif channel.is_nsfw():
        emoji_name = 'TEXT_NSFW'
    else:
        emoji_name = 'TEXT' if overwrites.read_messages else 'TEXT_LOCKED'

    return emojis.CHANNELS[emoji_name]


def badge_emojis(person: discord.User | discord.Member) -> str:
    badges = [badge for badge_name, badge in emojis.BADGES.items() if dict(person.public_flags)[badge_name] is True]

    if dict(person.public_flags)['verified_bot'] is False and person.bot:
        badges.append(emojis.BOT)

    if isinstance(person, discord.Member):
        if person.premium_since:
            badges.append(emojis.BOOSTER)
        if ((activity := discord.utils.find(lambda a: isinstance(a, discord.CustomActivity), person.activities)) is not None) and activity.emoji and activity.emoji.is_custom_emoji():
            badges.append(emojis.NITRO)

    if person.avatar.is_animated() and emojis.NITRO not in badges:
        badges.append(emojis.NITRO)

    return ' '.join(badges) if badges else 'N/A'


def activities(member: discord.Member) -> str:  # sourcery no-metrics

    if not member.activities:
        return '• N/A'

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

            album = f" from the album **{activity.album}**" if activity.album and activity.album != activity.title else ""
            message.append(f'• Listening to **[{activity.title}](https://open.spotify.com/track/{activity.track_id})** by **{", ".join(activity.artists)}** {album}')

        elif isinstance(activity, discord.Game):
            message.append(f'• Playing **{activity.name}**')

        elif isinstance(activity, discord.Streaming):
            message.append(f'• Streaming **[{activity.name}]({activity.url})** on **{activity.platform}**')

        else:
            message.append(f'• {f"{activity.emoji} " if activity.emoji else ""}{f"{activity.name}" if activity.name else ""}')

    return '\n'.join(message)


def avatar(person: discord.User | discord.Member, *, format: Optional[Literal['webp', 'jpeg', 'jpg', 'png', 'gif']] = None, size: int = 1024) -> Optional[str]:
    return str(person.avatar.replace(format=format or ('gif' if person.avatar.is_animated() else 'png'), size=size)) if person.avatar else None


def icon(guild: discord.Guild, *, format: Optional[Literal['webp', 'jpeg', 'jpg', 'png', 'gif']] = None, size: int = 1024) -> Optional[str]:
    return str(guild.icon.replace(format=format or ('gif' if guild.icon.is_animated() else 'png'), size=size)) if guild.icon else None


def banner(guild: discord.Guild, *, format: Optional[Literal['webp', 'jpeg', 'jpg', 'png', 'gif']] = None, size: int = 1024) -> Optional[str]:
    return str(guild.banner.replace(format=format or ('gif' if guild.banner.is_animated() else 'png'), size=size)) if guild.banner else None


def splash(guild: discord.Guild, *, format: Optional[Literal['webp', 'jpeg', 'jpg', 'png', 'gif']] = None, size: int = 1024) -> Optional[str]:
    return str(guild.splash.replace(format=format or ('gif' if guild.splash.is_animated() else 'png'), size=size)) if guild.splash else None


def format_command(command: commands.Command) -> str:
    return f'{config.PREFIX}{command.qualified_name}'


def voice_region(obj: discord.VoiceChannel | discord.StageChannel | discord.Guild) -> str:
    if not (region := obj.rtc_region if isinstance(obj, (discord.VoiceChannel, discord.StageChannel)) else obj.region):
        return 'Automatic'

    if region is discord.VoiceRegion.hongkong:
        region_name = 'Hong Kong'
    elif region is discord.VoiceRegion.southafrica:
        region_name = 'South Africa'
    else:
        region_name = obj.name.title().replace('Vip', 'VIP').replace('_', '-').replace('Us-', 'US-')

    return region_name


def name(person: discord.Member | discord.User, *, guild: Optional[discord.Guild] = None) -> str:
    if guild and isinstance(person, discord.User):
        member = guild.get_member(person.id)
        return member.nick or member.name if isinstance(member, discord.Member) else getattr(person, 'name', 'Unknown')

    return person.nick or person.name if isinstance(person, discord.Member) else getattr(person, 'name', 'Unknown')


#


async def upload_file(session: aiohttp.ClientSession, *, file_bytes: bytes | io.BytesIO, file_format: str) -> str:
    data = aiohttp.FormData()
    data.add_field('file', value=file_bytes, filename=f'file.{file_format.lower()}')

    async with session.post('https://cdn.axelancerr.xyz/api/media', headers={'Authorization': config.AXEL_WEB_TOKEN}, data=data) as response:

        if response.status == 413:
            raise exceptions.GeneralError('The image produced was too large to upload.')

        post = await response.json()

    return f'https://cdn.axelancerr.xyz/{post.get("filename")}'


async def safe_content(mystbin_client: mystbin.Client, content: str, *, syntax: str = 'txt', max_characters: int = 1024) -> str:
    if len(content) <= max_characters:
        return content

    try:
        paste = await mystbin_client.post(content, syntax=syntax)
        return paste.url
    except mystbin.APIError:
        return content[:max_characters]


#


def darken_colour(red: float, green: float, blue: float, factor: float = 0.1) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(red / 255.0, green / 255.0, blue / 255.0)
    red, green, blue = colorsys.hls_to_rgb(h, max(min(l * (1 - factor), 1.0), 0.0), s)
    return int(red * 255), int(green * 255), int(blue * 255)


def lighten_colour(red: float, green: float, blue: float, factor: float = 0.1) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(red / 255.0, green / 255.0, blue / 255.0)
    red, green, blue = colorsys.hls_to_rgb(h, max(min(l * (1 + factor), 1.0), 0.0), s)
    return int(red * 255), int(green * 255), int(blue * 255)


#


def embed(
        embed_footer_url: Optional[str] = None, embed_footer: Optional[str] = None, image: Optional[str] = None, thumbnail: Optional[str] = None, author: Optional[str] = None,
        author_url: Optional[str] = None, author_icon_url: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, url: Optional[str] = None,
        colour: discord.Colour = colours.MAIN, emoji: Optional[str] = None
) -> discord.Embed:
    embed = discord.Embed(colour=colour)

    if embed_footer:
        embed.set_footer(text=embed_footer, icon_url=embed_footer_url or discord.embeds.EmptyEmbed)

    if image:
        embed.set_image(url=image)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if author:
        embed.set_author(name=author, url=author_url or discord.embeds.EmptyEmbed, icon_url=author_icon_url or discord.embeds.EmptyEmbed)

    if title:
        embed.title = title
    if description:
        embed.description = f"{emoji} {values.ZWSP} {description}" if emoji else description
    if url:
        embed.url = url

    return embed


class _MissingSentinel:

    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return '...'


MISSING: Any = _MissingSentinel()
