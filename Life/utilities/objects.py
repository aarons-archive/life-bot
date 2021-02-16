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
import asyncio
import math
from typing import Dict, List, Optional

import discord
import pendulum
from pendulum import DateTime
from pendulum.tz.timezone import Timezone
from utilities import enums


class DefaultUserConfig:

    __slots__ = 'id', 'created_at', 'blacklisted', 'blacklisted_reason', 'colour', 'timezone', 'timezone_private', 'birthday', 'birthday_private', 'coins', 'xp', \
                'daily_collected', 'daily_streak', 'weekly_collected', 'weekly_streak', 'monthly_collected', 'monthly_streak', 'reminders', 'todos', 'requires_db_update'

    def __init__(self) -> None:

        self.id: int = 0
        self.created_at: DateTime = pendulum.now(tz='UTC')

        self.blacklisted: bool = False
        self.blacklisted_reason: Optional[str] = None

        self.colour: discord.Colour = discord.Colour.gold()

        self.timezone: Timezone = pendulum.timezone('UTC')
        self.timezone_private: bool = False

        self.birthday: DateTime = pendulum.DateTime(2020, 1, 1, tzinfo=pendulum.timezone('UTC'))
        self.birthday_private: bool = False

        self.coins: int = 0
        self.xp: int = 0

        self.daily_collected: DateTime = pendulum.now(tz='UTC')
        self.daily_streak: int = 0

        self.weekly_collected: DateTime = pendulum.now(tz='UTC')
        self.weekly_streak: int = 0

        self.monthly_collected: DateTime = pendulum.now(tz='UTC')
        self.monthly_streak: int = 0

        self.todos: Dict[int, Todo] = {}
        self.reminders: Dict[int, Reminder] = {}
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<DefaultUserConfig id=\'{self.id}\'>'


class UserConfig:

    __slots__ = 'id', 'created_at', 'blacklisted', 'blacklisted_reason', 'colour', 'timezone', 'timezone_private', 'birthday', 'birthday_private', 'coins', 'xp', \
                'daily_collected', 'daily_streak', 'weekly_collected', 'weekly_streak', 'monthly_collected', 'monthly_streak', 'reminders', 'todos', 'requires_db_update'

    def __init__(self, data: dict) -> None:

        self.id: int = data.get('id')
        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')

        self.blacklisted: bool = data.get('blacklisted')
        self.blacklisted_reason: Optional[str] = data.get('blacklisted_reason')

        self.colour: discord.Colour = discord.Colour(int(data.get('colour'), 16))

        self.timezone: Timezone = pendulum.timezone(data.get('timezone'))
        self.timezone_private: bool = data.get('timezone_private')

        self.birthday: DateTime = pendulum.parse(data.get('birthday').isoformat(), tz='UTC')
        self.birthday_private: bool = data.get('birthday_private')

        self.coins: int = data.get('coins')
        self.xp: int = data.get('xp')

        self.daily_collected: DateTime = pendulum.instance(data.get('daily_collected'), tz='UTC')
        self.daily_streak: int = data.get('daily_streak')

        self.weekly_collected: DateTime = pendulum.instance(data.get('weekly_collected'), tz='UTC')
        self.weekly_streak: int = data.get('weekly_streak')

        self.monthly_collected: DateTime = pendulum.instance(data.get('monthly_collected'), tz='UTC')
        self.monthly_streak: int = data.get('monthly_streak')

        self.todos: Dict[int, Todo] = {}
        self.reminders: Dict[int, Reminder] = {}
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<UserConfig id=\'{self.id}\' blacklisted={self.blacklisted} colour={self.colour} xp={self.xp} level={self.level}>'

    @property
    def time(self) -> DateTime:
        return pendulum.now(tz=self.timezone)

    @property
    def age(self) -> int:
        return (pendulum.now(tz='UTC') - self.birthday).in_years()

    @property
    def next_birthday(self) -> pendulum.datetime:
        return self.birthday.replace(year=self.birthday.year + self.age + 1)

    @property
    def level(self) -> int:
        return math.floor((((self.xp / 100) ** (1.0 / 1.5)) / 3))

    @property
    def next_level_xp(self) -> int:
        return round((((((self.level + 1) * 3) ** 1.5) * 100) - self.xp))


# noinspection PyArgumentList
class DefaultGuildConfig:

    __slots__ = 'id', 'created_at', 'blacklisted', 'blacklisted_reason', 'colour', 'embed_size', 'prefixes', 'tags', 'requires_db_update'

    def __init__(self) -> None:

        self.id: int = 0
        self.created_at: DateTime = pendulum.now(tz='UTC')

        self.blacklisted: bool = False
        self.blacklisted_reason: Optional[str] = None

        self.colour: discord.Colour = discord.Colour.gold()
        self.embed_size: enums.EmbedSize = enums.EmbedSize(0)
        self.prefixes: List[str] = []

        self.tags: Dict[str, Tag] = {}
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<DefaultGuildConfig id=\'{self.id}\'>'


# noinspection PyArgumentList
class GuildConfig:

    __slots__ = 'id', 'created_at', 'blacklisted', 'blacklisted_reason', 'colour', 'embed_size', 'prefixes', 'tags', 'requires_db_update'

    def __init__(self, data: dict) -> None:

        self.id: int = data.get('id')
        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')

        self.blacklisted: bool = data.get('blacklisted')
        self.blacklisted_reason: Optional[str] = data.get('blacklisted_reason')

        self.colour: discord.Colour = discord.Colour(int(data.get('colour'), 16))
        self.embed_size = enums.EmbedSize(data.get('embed_size'))
        self.prefixes: List[str] = data.get('prefixes')

        self.tags: Dict[str, Tag] = {}
        self.requires_db_update = []

    def __repr__(self) -> str:
        return f'<GuildConfig id=\'{self.id}\' blacklisted={self.blacklisted} colour={self.colour}>'


class Reminder:

    __slots__ = 'id', 'user_id', 'created_at', 'datetime', 'content', 'jump_url', 'task'

    def __init__(self, data: dict) -> None:

        self.id: int = data.get('id')
        self.user_id: int = data.get('user_id')
        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')
        self.datetime: DateTime = pendulum.instance(data.get('datetime'), tz='UTC')
        self.content: str = data.get('content')
        self.jump_url: str = data.get('jump_url')

        self.task: Optional[asyncio.Task] = None

    def __repr__(self) -> str:
        return f'<Reminder id=\'{self.id}\' user_id=\'{self.user_id}\' datetime={self.datetime} done={self.done}>'

    @property
    def done(self) -> bool:
        return pendulum.now(tz='UTC') > self.datetime


class Tag:

    __slots__ = 'id', 'user_id', 'guild_id', 'created_at', 'name', 'alias', 'content', 'jump_url'

    def __init__(self, data: dict) -> None:

        self.id: int = data.get('id')
        self.user_id: int = data.get('user_id')
        self.guild_id: int = data.get('guild_id')
        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')
        self.name: str = data.get('name')
        self.alias: Optional[str] = data.get('alias')
        self.content: str = data.get('content')
        self.jump_url: Optional[str] = data.get('jump_url')

    def __repr__(self) -> str:
        return f'<Tag id=\'{self.id}\' user_id=\'{self.user_id}\' guild_id=\'{self.guild_id}\' name=\'{self.name}\' alias=\'{self.alias}\'>'


class Todo:

    __slots__ = 'id', 'user_id', 'created_at', 'content', 'jump_url'

    def __init__(self, data: dict) -> None:

        self.id: int = data.get('id')
        self.user_id: int = data.get('user_id')
        self.created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')
        self.content: str = data.get('content')
        self.jump_url: Optional[str] = data.get('jump_url')

    def __repr__(self) -> str:
        return f'<Todo id=\'{self.id}\' user_id=\'{self.user_id}\'>'