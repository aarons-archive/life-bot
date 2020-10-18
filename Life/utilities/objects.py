"""
Life
Copyright (C) 2020 Axel#3456

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""
import math

import discord
import pendulum


class DefaultGuildConfig:

    __slots__ = ('prefixes', 'colour', 'blacklisted', 'blacklisted_reason')

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()
        self.prefixes = []

        self.blacklisted = False
        self.blacklisted_reason = 'None'

    def __repr__(self) -> str:
        return f'<DefaultGuildConfig colour=\'{self.colour}\' prefixes={self.prefixes}>'


class GuildConfig:

    __slots__ = ('prefixes', 'colour', 'blacklisted', 'blacklisted_reason')

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))
        self.prefixes = data.get('prefixes')

        self.blacklisted = data.get('blacklisted')
        self.blacklisted_reason = data.get('blacklisted_reason')

    def __repr__(self) -> str:
        return f'<GuildConfig colour=\'{self.colour}\' prefixes={self.prefixes}>'


class DefaultUserConfig:

    __slots__ = ('colour', 'coins', 'xp', 'timezone', 'timezone_private', 'blacklisted', 'blacklisted_reason', 'requires_db_update', 'level_up_notifications')

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()
        self.coins = 0
        self.xp = 0

        self.timezone = pendulum.timezone('UTC')
        self.timezone_private = False

        self.blacklisted = False
        self.blacklisted_reason = 'None'

        self.level_up_notifications = False

        self.requires_db_update = False

    def __repr__(self) -> str:
        return f'<DefaultUserConfig colour=\'{self.colour}\' coins={self.coins}>'

    @property
    def time(self) -> pendulum.datetime:
        return pendulum.now(tz=self.timezone)

    @property
    def level(self) -> int:
        return math.floor((((self.xp / 100) ** (1.0 / 1.5)) / 3))

    @property
    def next_level_xp(self) -> int:
        return round((((((self.level + 1) * 3) ** 1.5) * 100) - self.xp))


class UserConfig:

    __slots__ = ('colour', 'coins', 'xp', 'timezone', 'timezone_private', 'blacklisted', 'blacklisted_reason', 'requires_db_update', 'level_up_notifications')

    def __init__(self, data: dict) -> None:
        self.colour = discord.Colour(int(data.get('colour'), 16))
        self.coins = data.get('coins')
        self.xp = data.get('xp')

        self.timezone = pendulum.timezone(data.get('timezone'))
        self.timezone_private = data.get('timezone_private')

        self.blacklisted = data.get('blacklisted')
        self.blacklisted_reason = data.get('blacklisted_reason')

        self.level_up_notifications = data.get('level_up_notifications')

        self.requires_db_update = False

    def __repr__(self) -> str:
        return f'<UserConfig colour=\'{self.colour}\' coins={self.coins}>'

    @property
    def time(self) -> pendulum.datetime:
        return pendulum.now(tz=self.timezone)

    @property
    def level(self) -> int:
        return math.floor((((self.xp / 100) ** (1.0 / 1.5)) / 3))

    @property
    def next_level_xp(self) -> int:
        return round((((((self.level + 1) * 3) ** 1.5) * 100) - self.xp))
