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
from typing import Dict, List, Optional

import discord
import pendulum
from pendulum import DateTime
from pendulum.tz.timezone import Timezone


class DefaultUserConfig:

    __slots__ = 'id', 'colour', 'blacklisted', 'blacklisted_reason', 'timezone', 'timezone_private', 'birthday', 'birthday_private', 'xp', 'coins', 'level_up_notifications', \
                'daily_collected', 'daily_streak', 'weekly_collected', 'weekly_streak', 'monthly_collected', 'monthly_streak', 'spotify_refresh_token', 'created_at', 'reminders', \
                'requires_db_update'

    def __init__(self) -> None:

        self.id: int = 0

        self.colour: discord.Colour = discord.Colour.gold()

        self.blacklisted: bool = False
        self.blacklisted_reason: str = 'None'

        self.timezone: Timezone = pendulum.timezone('UTC')
        self.timezone_private: bool = False

        self.birthday: DateTime = pendulum.DateTime(2020, 1, 1, tzinfo=pendulum.timezone('UTC'))
        self.birthday_private: bool = False

        self.xp: int = 0
        self.coins: int = 0

        self.level_up_notifications: bool = False

        self.daily_collected: DateTime = pendulum.now(tz='UTC')
        self.daily_streak: int = 0

        self.weekly_collected: DateTime = pendulum.now(tz='UTC')
        self.weekly_streak: int = 0

        self.monthly_collected: DateTime = pendulum.now(tz='UTC')
        self.monthly_streak: int = 0

        self.spotify_refresh_token: Optional[str] = None

        self.created_at: DateTime = pendulum.now(tz='UTC')

        self.reminders: List[Optional[Reminder]] = []
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<DefaultUserConfig id=\'{self.id}\' colour=\'{self.colour}\' coins={self.coins}>'

    @property
    def age(self) -> int:
        return (pendulum.now(tz="UTC") - self.birthday).in_years()

    @property
    def next_birthday(self) -> pendulum.datetime:
        return self.birthday.replace(year=self.birthday.year + self.age + 1)

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

    __slots__ = 'id', 'colour', 'blacklisted', 'blacklisted_reason', 'timezone', 'timezone_private', 'birthday', 'birthday_private', 'xp', 'coins', 'level_up_notifications', \
                'daily_collected', 'daily_streak', 'weekly_collected', 'weekly_streak', 'monthly_collected', 'monthly_streak', 'spotify_refresh_token', 'created_at', 'reminders', \
                'requires_db_update'

    def __init__(self, data: dict) -> None:

        self.id: int = data.get('id', 0)

        self.colour: discord.Colour = discord.Colour(int(data.get('colour'), 16))

        self.blacklisted: bool = data.get('blacklisted')
        self.blacklisted_reason: str = data.get('blacklisted_reason')

        self.timezone: Timezone = pendulum.timezone(data.get('timezone'))
        self.timezone_private: bool = data.get('timezone_private')

        self.birthday: DateTime = pendulum.parse(data.get('birthday').isoformat(), tz='UTC')
        self.birthday_private: bool = data.get('birthday_private')

        self.xp: int = data.get('xp')
        self.coins: int = data.get('coins')

        self.level_up_notifications: bool = data.get('level_up_notifications')

        self.daily_collected: DateTime = pendulum.instance(data.get('daily_collected'), tz='UTC')
        self.daily_streak: int = data.get('daily_streak')

        self.weekly_collected: DateTime = pendulum.instance(data.get('weekly_collected'), tz='UTC')
        self.weekly_streak: int = data.get('weekly_streak')

        self.monthly_collected: DateTime = pendulum.instance(data.get('monthly_collected'), tz='UTC')
        self.monthly_streak: int = data.get('monthly_streak')

        self.spotify_refresh_token: Optional[str] = data.get('spotify_refresh_token')

        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')

        self.reminders: List[Optional[Reminder]] = []
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<UserConfig id=\'{self.id}\' colour=\'{self.colour}\' coins={self.coins}>'

    @property
    def age(self) -> int:
        return (pendulum.now(tz="UTC") - self.birthday).in_years()

    @property
    def next_birthday(self) -> pendulum.datetime:
        return self.birthday.replace(year=self.birthday.year + self.age + 1)

    @property
    def time(self) -> pendulum.datetime:
        return pendulum.now(tz=self.timezone)

    @property
    def level(self) -> int:
        return math.floor((((self.xp / 100) ** (1.0 / 1.5)) / 3))

    @property
    def next_level_xp(self) -> int:
        return round((((((self.level + 1) * 3) ** 1.5) * 100) - self.xp))


class DefaultGuildConfig:

    __slots__ = 'prefixes', 'colour', 'blacklisted', 'blacklisted_reason', 'embed_size', 'tags', 'requires_db_update'

    def __init__(self) -> None:

        self.colour = discord.Colour.gold()
        self.prefixes = []

        self.blacklisted = False
        self.blacklisted_reason = 'None'

        self.embed_size = 'normal'

        self.tags: Dict[str, Tag] = {}
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<DefaultGuildConfig colour=\'{self.colour}\' prefixes={self.prefixes}>'


class GuildConfig:

    __slots__ = 'prefixes', 'colour', 'blacklisted', 'blacklisted_reason', 'embed_size', 'tags', 'requires_db_update'

    def __init__(self, data: dict) -> None:

        self.colour = discord.Colour(int(data.get('colour'), 16))
        self.prefixes = data.get('prefixes')

        self.blacklisted = data.get('blacklisted')
        self.blacklisted_reason = data.get('blacklisted_reason')

        self.embed_size = data.get('embed_size')

        self.tags: Dict[str, Tag] = {}
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<GuildConfig colour=\'{self.colour}\' prefixes={self.prefixes}>'


class Tag:

    __slots__ = 'owner_id', 'guild_id', 'name', 'content', 'alias', 'created_at', 'jump_link'

    def __init__(self, data: dict) -> None:

        self.owner_id: int = data.get('owner_id')
        self.guild_id: int = data.get('guild_id')
        self.name: str = data.get('name')
        self.content: str = data.get('content')
        self.alias: str = data.get('alias')
        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')
        self.jump_link: str = data.get('jump_link')

    def __repr__(self) -> str:
        return f'<Tag owner_id=\'{self.owner_id}\' guild_id=\'{self.guild_id}\' name=\'{self.name}\' alias=\'{self.alias}\'>'


class Reminder:

    __slots__ = 'user_id', 'channel_id', 'message_id', 'id', 'datetime', 'created_at', 'content', 'link', 'dm', 'task'

    def __init__(self, data: dict) -> None:

        self.user_id = data.get('user_id')
        self.channel_id = data.get('channel_id')
        self.message_id = data.get('message_id')
        self.id = data.get('id')
        self.datetime = pendulum.instance(data.get('datetime'), tz='UTC')
        self.created_at = pendulum.instance(data.get('created_at'), tz='UTC')
        self.content = data.get('content')
        self.link = data.get('link')
        self.dm = data.get('dm')

        self.task = None

    def __repr__(self) -> str:
        return f'<Reminder user_id={self.user_id} id={self.id} datetime={self.datetime} done={self.done}>'

    @property
    def done(self) -> bool:
        return pendulum.now(tz='UTC') > self.datetime
