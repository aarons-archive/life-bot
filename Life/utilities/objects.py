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

import math

import discord
import pendulum


class DefaultGuildConfig:

    __slots__ = ('prefixes', 'colour', 'blacklisted', 'blacklisted_reason', 'requires_db_update')

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()
        self.prefixes = []

        self.blacklisted = False
        self.blacklisted_reason = 'None'

        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<DefaultGuildConfig colour=\'{self.colour}\' prefixes={self.prefixes}>'


class GuildConfig:

    __slots__ = ('prefixes', 'colour', 'blacklisted', 'blacklisted_reason', 'requires_db_update')

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))
        self.prefixes = data.get('prefixes')

        self.blacklisted = data.get('blacklisted')
        self.blacklisted_reason = data.get('blacklisted_reason')

        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<GuildConfig colour=\'{self.colour}\' prefixes={self.prefixes}>'


class DefaultUserConfig:

    __slots__ = ('colour', 'blacklisted', 'blacklisted_reason', 'timezone', 'timezone_private', 'coins', 'xp', 'level_up_notifications', 'requires_db_update',
                 'daily_collected', 'weekly_collected', 'monthly_collected', 'daily_streak', 'weekly_streak', 'monthly_streak')

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()

        self.blacklisted = False
        self.blacklisted_reason = 'None'

        self.timezone = pendulum.timezone('UTC')
        self.timezone_private = False

        self.xp = 0
        self.coins = 0

        self.level_up_notifications = False

        self.daily_collected = pendulum.now(tz='UTC')
        self.weekly_collected = pendulum.now(tz='UTC')
        self.monthly_collected = pendulum.now(tz='UTC')

        self.daily_streak = 0
        self.weekly_streak = 0
        self.monthly_streak = 0

        self.requires_db_update = []

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

    __slots__ = ('colour', 'blacklisted', 'blacklisted_reason', 'timezone', 'timezone_private', 'coins', 'xp', 'level_up_notifications', 'requires_db_update',
                 'daily_collected', 'weekly_collected', 'monthly_collected', 'daily_streak', 'weekly_streak', 'monthly_streak')

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))

        self.blacklisted = data.get('blacklisted')
        self.blacklisted_reason = data.get('blacklisted_reason')

        self.timezone = pendulum.timezone(data.get('timezone'))
        self.timezone_private = data.get('timezone_private')

        self.xp = data.get('xp')
        self.coins = data.get('coins')

        self.level_up_notifications = data.get('level_up_notifications')

        self.daily_collected = data.get('daily_collected')
        self.weekly_collected = data.get('weekly_collected')
        self.monthly_collected = data.get('monthly_collected')

        self.daily_streak = data.get('daily_streak')
        self.weekly_streak = data.get('weekly_streak')
        self.monthly_streak = data.get('monthly_streak')

        self.requires_db_update = []

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
