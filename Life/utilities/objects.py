"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import discord
import pytz


class DefaultGuildConfig:

    __slots__ = ('prefixes', 'colour', 'starboard_channel', 'starboard_threshold')

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()
        self.prefixes = []
        self.starboard_channel = None
        self.starboard_threshold = 3

    def __repr__(self) -> str:
        return f'<DefaultGuildConfig colour={self.colour} prefixes={self.prefixes} >'


class GuildConfig:

    __slots__ = ('prefixes', 'colour', 'starboard_channel', 'starboard_threshold')

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))
        self.prefixes = data.get('prefixes')
        self.starboard_channel = data.get('starboard_channel')
        self.starboard_threshold = data.get('starboard_threshold')

    def __repr__(self) -> str:
        return f'<GuildConfig colour={self.colour} prefixes={self.prefixes} >'


class DefaultUserConfig:

    __slots__ = ('colour', 'money', 'timezone', 'timezone_private')

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()
        self.money = 0
        self.timezone = 'UTC'
        self.timezone_private = False

    def __repr__(self) -> str:
        timezone = f'timezone=\'{self.timezone}\'' if self.timezone_private is False else ''
        return f'<DefaultUserConfig colour=\'{self.colour}\' money={self.money} timezone_private={self.timezone_private} {timezone}>'

    @property
    def pytz(self):
        return pytz.timezone(self.timezone)


class UserConfig:

    __slots__ = ('colour', 'money', 'timezone', 'timezone_private')

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))
        self.money = data.get('money')
        self.timezone = data.get('timezone')
        self.timezone_private = data.get('timezone_private')

    def __repr__(self) -> str:
        timezone = f'timezone=\'{self.timezone}\'' if self.timezone_private is False else ''
        return f'<UserConfig colour=\'{self.colour}\' money={self.money} timezone_private={self.timezone_private} {timezone}>'

    @property
    def pytz(self):
        return pytz.timezone(self.timezone)
