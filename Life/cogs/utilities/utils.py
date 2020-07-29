"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see <https://www.gnu.org/licenses/>.
"""

import typing

import discord

from cogs.utilities import objects


class Utils:

    def __init__(self, bot):
        self.bot = bot

    def try_int(self, string: str) -> typing.Union[int, str]:
        try:
            return int(string)
        except ValueError:
            return str(string)

    def format_time(self, seconds: int, friendly: bool = False) -> str:

        minute, second = divmod(seconds, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)

        days, hours, minutes, seconds, = round(day), round(hour), round(minute), round(second)

        if friendly is True:
            formatted = f'{minutes}m {seconds}s'
            if not hours == 0:
                formatted = f'{hours}h {formatted}'
            if not days == 0:
                formatted = f'{days}d {formatted}'
        else:
            formatted = f'{minutes:02d}:{seconds:02d}'
            if not hours == 0:
                formatted = f'{hours:02d}:{formatted}'
            if not days == 0:
                formatted = f'{days:02d}:{formatted}'

        return formatted

    def guild_config(self, guild: discord.Guild) -> typing.Union[objects.DefaultGuildConfig, objects.GuildConfig]:

        guild_config = self.bot.guild_configs.get(guild.id)
        if not guild_config:
            return self.bot.default_guild_config

        return guild_config
