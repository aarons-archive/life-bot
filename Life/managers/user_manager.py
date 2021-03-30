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

import io
import logging
import math
import os
from typing import List, Literal, TYPE_CHECKING, Union

import discord
import pendulum
from PIL import Image, ImageDraw, ImageFont
from discord.ext import tasks
from pendulum import DateTime

from utilities import enums, exceptions, objects

if TYPE_CHECKING:
    from bot import Life

__log__ = logging.getLogger(__name__)


class UserManager:

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.default_config = objects.DefaultUserConfig()
        self.configs = {}

        self.update_database.start()

    async def load(self) -> None:

        configs = await self.bot.db.fetch('SELECT * FROM users')
        for config in configs:
            self.configs[config['id']] = objects.UserConfig(data=config)

        __log__.info(f'[USER MANAGER] Loaded user configs. [{len(configs)} users]')
        print(f'[USER MANAGER] Loaded user configs. [{len(configs)} users]')

        await self.bot.reminder_manager.load()
        await self.bot.todo_manager.load()

    #

    @tasks.loop(seconds=60)
    async def update_database(self) -> None:

        if not self.configs:
            return

        need_updating = {user_id: user_config for user_id, user_config in self.configs.items() if len(user_config.requires_db_update) >= 1}

        async with self.bot.db.acquire(timeout=300) as db:
            for user_id, user_config in need_updating.items():

                query = ','.join(f'{editable.value} = ${index + 2}' for index, editable in enumerate(user_config.requires_db_update))
                await db.execute(f'UPDATE users SET {query} WHERE id = $1', user_id, *[getattr(user_config, attribute.value) for attribute in user_config.requires_db_update])

                user_config.requires_db_update = set()

    @update_database.before_loop
    async def before_update_database(self) -> None:
        await self.bot.wait_until_ready()

    #

    async def create_config(self, *, user_id: int) -> objects.UserConfig:

        data = await self.bot.db.fetchrow('INSERT INTO users (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *', user_id)
        self.configs[user_id] = objects.UserConfig(data=data)

        __log__.info(f'[USER MANAGER] Created config for user with id \'{user_id}\'')
        return self.configs[user_id]

    async def get_or_create_config(self, *, user_id: int) -> objects.UserConfig:

        if isinstance(user_config := self.get_config(user_id=user_id), objects.DefaultUserConfig):
            user_config = await self.create_config(user_id=user_id)

        return user_config

    def get_config(self, *, user_id: int) -> Union[objects.DefaultUserConfig, objects.UserConfig]:
        return self.configs.get(user_id, self.default_config)

    #

    async def set_blacklisted(self, *, user_id: int, blacklisted: bool = True, reason: str = None) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)

        query = 'UPDATE users SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $3 RETURNING blacklisted, blacklisted_reason'
        data = await self.bot.db.fetchrow(query, blacklisted, reason, user_id)
        user_config.blacklisted = data['blacklisted']
        user_config.blacklisted_reason = data['blacklisted_reason']

    async def set_colour(self, *, user_id: int, colour: str = str(discord.Colour.gold())) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)

        data = await self.bot.db.fetchrow('UPDATE users SET colour = $1 WHERE id = $2', f'0x{colour.strip("#")}', user_id)
        user_config.colour = discord.Colour(int(data['colour'], 16))

    async def set_timezone(self, *, user_id: int, timezone: str = None, private: bool = None) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)
        timezone = str(user_config.timezone) if timezone is None else timezone
        private = user_config.timezone_private if private is None else private

        data = await self.bot.db.fetchrow('UPDATE users SET timezone = $1, timezone_private = $2 WHERE id = $3 RETURNING timezone, timezone_private', timezone, private, user_id)
        user_config.timezone = pendulum.timezone(data['timezone'])
        user_config.timezone_private = private

    async def set_birthday(self, *, user_id: int, birthday: pendulum.datetime = None, private: bool = None) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)
        birthday = user_config.birthday if birthday is None else birthday
        private = user_config.timezone_private if private is None else private

        data = await self.bot.db.fetchrow('UPDATE users SET birthday = $1, birthday_private = $2 WHERE id = $3 RETURNING birthday, birthday_private', birthday, private, user_id)
        user_config.birthday = pendulum.parse(data['birthday'].isoformat(), tz='UTC')
        user_config.birthday_private = private

    async def set_coins(self, *, user_id: int, coins: int, operation: enums.Operation = enums.Operation.ADD) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)

        if operation == enums.Operation.SET:
            user_config.coins = coins
        elif operation == enums.Operation.ADD:
            user_config.coins += coins
        elif operation == enums.Operation.MINUS:
            user_config.coins -= coins

        user_config.requires_db_update.add(enums.Updateable.COINS)

    async def set_xp(self, *, user_id: int, xp: int, operation: enums.Operation = enums.Operation.ADD) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)

        if operation == enums.Operation.SET:
            user_config.xp = xp
        elif operation == enums.Operation.ADD:
            user_config.xp += xp
        elif operation == enums.Operation.MINUS:
            user_config.xp -= xp

        user_config.requires_db_update.add(enums.Updateable.XP)

    async def set_bundle_collection(
            self, *, user_id: int, type: Union[enums.Updateable.DAILY_COLLECTED, enums.Updateable.WEEKLY_COLLECTED, enums.Updateable.MONTHLY_COLLECTED],
            when: DateTime = pendulum.now(tz='UTC')
    ) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)

        data = await self.bot.db.fetchrow(f'UPDATE users SET {type.value} = $1 WHERE id = $2 RETURNING {type.value}', when, user_id)
        setattr(user_config, type.value, pendulum.instance(data[type.value], tz='UTC'))

    async def set_bundle_streak(
            self, *, user_id: int, type: Union[enums.Updateable.DAILY_STREAK, enums.Updateable.WEEKLY_STREAK, enums.Updateable.MONTHLY_STREAK],
            operation: enums.Operation = enums.Operation.SET, count: int = 0
    ) -> None:

        user_config = await self.get_or_create_config(user_id=user_id)

        streak = None
        if operation == enums.Operation.SET:
            streak = count
        elif operation == enums.Operation.ADD:
            streak = getattr(user_config, type.value) + count
        elif operation == enums.Operation.MINUS:
            streak = getattr(user_config, type.value) - count
        elif operation == enums.Operation.RESET:
            streak = 0

        data = await self.bot.db.fetchrow(f'UPDATE users SET {type.value} = $1 WHERE id = $2 RETURNING {type.value}', streak, user_id)
        setattr(user_config, type.value, data[type.value])

    #

    async def create_timecard(self, *, guild_id: int) -> io.BytesIO:

        guild = self.bot.get_guild(guild_id)
        if not guild:
            raise exceptions.ArgumentError('Guild with that id not found.')

        configs = sorted(self.configs.items(), key=lambda kv: kv[1].time.offset_hours)
        timezone_users = {}

        for user_id, config in configs:

            if config.timezone_private or config.timezone == pendulum.timezone('UTC'):
                continue

            user = guild.get_member(user_id)
            if not user:
                continue

            if timezone_users.get(config.time.format('HH:mm (ZZ)')) is None:
                timezone_users[config.time.format('HH:mm (ZZ)')] = [io.BytesIO(await user.avatar_url_as(format='png', size=256).read())]

            else:
                timezone_users[config.time.format('HH:mm (ZZ)')].append(io.BytesIO(await user.avatar_url_as(format='png', size=256).read()))

        if not timezone_users:
            raise exceptions.ArgumentError('There are no users with timezones set in this server.')

        buffer = await self.bot.loop.run_in_executor(None, self.create_timecard_image, timezone_users)
        return buffer

    @staticmethod
    def create_timecard_image(timezone_users: dict) -> io.BytesIO:

        width_x = (1600 * (len(timezone_users.keys()) if len(timezone_users.keys()) < 5 else 5)) + 100
        height_y = (1800 * math.ceil(len(timezone_users.keys()) / 5)) + 100

        image = Image.new('RGBA', (width_x, height_y), color='#f1c30f')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/arial.ttf')), 120)

        x = 100
        y = 100

        for timezone, users in timezone_users.items():

            draw.text((x, y), timezone, font=font, fill='#1b1a1c')

            user_x = x
            user_y = y + 200

            for user in users[:36]:

                avatar = Image.open(user)
                avatar = avatar.resize((250, 250))

                image.paste(avatar, (user_x, user_y))

                if user_x < x + 1200:
                    user_x += 250
                else:
                    user_y += 250
                    user_x = x

            if x > 6400:
                y += 1800
                x = 100
            else:
                x += 1600

        buffer = io.BytesIO()
        image.save(buffer, 'png')
        buffer.seek(0)

        image.close()
        return buffer

    #

    def leaderboard(self, *, guild_id: int = None, type: Literal['level', 'xp', 'coins']) -> List[objects.UserConfig]:

        if not guild_id:
            configs = filter(lambda kv: self.bot.get_user(kv[1].id) is not None and getattr(kv[1], type) != 0, self.configs.items())

        else:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                raise exceptions.ArgumentError('Guild with that id not found.')

            configs = filter(lambda kv: guild.get_member(kv[1].id) is not None and getattr(kv[1], type) != 0, self.configs.items())

        return sorted(configs, key=lambda kv: getattr(kv[1], type), reverse=True)

    def rank(self, *, user_id: int, guild_id: int = None) -> int:

        if not guild_id:
            configs = dict(sorted(self.configs.items(), key=lambda kv: kv[1].xp, reverse=True))

        else:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                raise exceptions.ArgumentError('Guild with that id not found.')

            configs = dict(sorted(filter(lambda kv: guild.get_member(kv[1].id) is not None and kv[1].xp != 0, self.configs.items()), key=lambda kv: kv[1].xp, reverse=True))

        try:
            return list(configs.keys()).index(user_id) + 1
        except ValueError:
            raise exceptions.ArgumentError('That user does not have a rank yet.')
