"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

import codecs
import os
import pathlib
import random
import collections
import time

import discord
from discord.ext import commands


class Utils:

    def __init__(self, bot):
        self.bot = bot

        self.colours = {
            discord.Status.online: 0x008000,
            discord.Status.idle: 0xFF8000,
            discord.Status.dnd: 0xFF0000,
            discord.Status.offline: 0x808080,
            discord.Status.invisible: 0x808080,
        }

        self.mfa_levels = {
            0: 'Not required',
            1: 'Required'
        }

        self.verification_levels = {
            discord.VerificationLevel.none: 'None - No criteria set.',
            discord.VerificationLevel.low: 'Low - Must have a verified email.',
            discord.VerificationLevel.medium: 'Medium - Must have a verified email and be registered on discord for '
                                              'more than 5 minutes.',
            discord.VerificationLevel.high: 'High - Must have a verified email, be registered on discord for more '
                                            'than 5 minutes and be a member of the guild for more then 10 minutes.',
            discord.VerificationLevel.extreme: 'Extreme - Must have a verified email, be registered on discord for '
                                               'more than 5 minutes, be a member of the guild for more then 10 minutes '
                                               'and a have a verified phone number.'
        }

        self.content_filter_levels = {
            discord.ContentFilter.disabled: 'None',
            discord.ContentFilter.no_role: 'No roles',
            discord.ContentFilter.all_members: 'All members',
        }

    async def ping(self, ctx: commands.Context):

        latency_ms = f'{round(self.bot.latency * 1000)}ms'

        typing_start = time.monotonic()
        await ctx.trigger_typing()
        typing_end = time.monotonic()
        typing_ms = f'{round((typing_end - typing_start) * 1000)}ms'

        discord_start = time.monotonic()
        async with self.bot.session.get('https://discordapp.com/') as resp:
            if resp.status == 200:
                discord_end = time.monotonic()
                discord_ms = f'{round((discord_end - discord_start) * 1000)}ms'
            else:
                discord_ms = 'Failed'

        return latency_ms, typing_ms, discord_ms

    def linecount(self):

        docstring = False
        file_amount, functions, lines, classes = 0, 0, 0, 0

        for dirpath, dirname, filenames in os.walk('.'):
            for name in filenames:

                if not name.endswith('.py'):
                    continue
                file_amount += 1

                # noinspection PyArgumentEqualDefault
                with codecs.open('./' + str(pathlib.PurePath(dirpath, name)), 'r', 'utf-8') as files_lines:
                    for line in files_lines:
                        line = line.strip()
                        if len(line) == 0:
                            continue
                        elif line.startswith("'''"):
                            if docstring is False:
                                docstring = True
                            else:
                                docstring = False
                        elif docstring is True:
                            continue
                        if line.startswith('#'):
                            continue
                        if line.startswith(('def', 'async def')):
                            functions += 1
                        if line.startswith('class'):
                            classes += 1
                        lines += 1

        return file_amount, functions, lines, classes

    def format_time(self, seconds: int, friendly: bool = False):

        minute, second = divmod(seconds, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)

        days, hours, minutes, seconds, = round(day), round(hour), round(minute), round(second)

        if friendly is True:
            formatted = f'{days}d {hours}h {minutes}m {seconds}s'
        else:
            formatted = f'{minutes:02d}:{seconds:02d}'
            if not hours == 0:
                formatted = f'{hours:02d}:{formatted}'
            if not days == 0:
                formatted = f'{days:02d}:{formatted}'

        return formatted

    def try_int(self, string: str):
        try:
            return int(string)
        except ValueError:
            return str(string)

    def random_colour(self):
        return '#%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def member_activity(self, member: discord.Member):

        if not member.activity or not member.activities:
            return 'N/A'

        message = '\n'

        for activity in member.activities:

            if activity.type == discord.ActivityType.custom:
                message += f'• '
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
                    if activity.album and not activity.album == activity.title:
                        message += f'from the album **{activity.album}** '
                    message += '\n'
                else:
                    message += f'• Listening to **{activity.name}**\n'

        return message

    def member_status(self, member: discord.Member):
        return member.status.name.replace('dnd', 'Do Not Disturb').title()

    def member_colour(self, member: discord.Member):
        return self.colours[member.status]

    def member_avatar(self, member: discord.Member):
        return str(member.avatar_url_as(format='gif' if member.is_avatar_animated() is True else 'png'))

    def guild_icon(self, guild: discord.Guild):
        return str(guild.icon_url_as(format='gif' if guild.is_icon_animated() is True else 'png'))

    def guild_banner(self, guild: discord.Guild):
        return str(guild.banner_url_as(format='png'))

    def guild_region(self, guild: discord.Guild):

        if guild.region == discord.VoiceRegion.hongkong:
            return 'Hong Kong'
        if guild.region == discord.VoiceRegion.southafrica:
            return 'South Africa'

        return guild.region.name.title().replace('Vip', 'VIP').replace('_', '-')

    def content_filter_level(self, guild: discord.Guild):
        return self.content_filter_levels[guild.explicit_content_filter]

    def verification_level(self, guild: discord.Guild):
        return self.verification_levels[guild.verification_level]

    def mfa_level(self, guild: discord.Guild):
        return self.mfa_levels[guild.mfa_level]

    def guild_member_status(self, guild: discord.Guild, all_guilds: bool = False):

        if all_guilds is True:
            members = [member for members in [guild.members for guild in self.bot.guilds] for member in members]
        else:
            members = guild.members

        statuses = collections.Counter()

        for member in members:

            statuses[member.status.name] += 1

            activities = [activity for activity in member.activities if activity.type == discord.ActivityType.streaming]
            if activities:
                statuses[activities[0].type.name] += 1

        return statuses
