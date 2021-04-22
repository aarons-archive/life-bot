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
import pathlib
import random
from typing import Literal, TYPE_CHECKING, Union

import discord
import pendulum
from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief
from discord.ext import tasks
from pendulum import DateTime

from utilities import enums, exceptions, objects, utils

if TYPE_CHECKING:
    from bot import Life

__log__ = logging.getLogger(__name__)


class UserManager:

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.default_config = objects.DefaultUserConfig()
        self.configs = {}

        self.update_database.start()

        self.IMAGES = {
            'SAI': {
                'level_cards': [
                    pathlib.Path('./resources/SAI/level_cards/1.png'),
                    pathlib.Path('./resources/SAI/level_cards/2.png'),
                    pathlib.Path('./resources/SAI/level_cards/3.png'),
                    pathlib.Path('./resources/SAI/level_cards/4.png'),
                ]
            }
        }

        self.ARIAL_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/fonts/arial.ttf'))
        self.KABEL_BLACK_FONT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources/fonts/kabel_black.otf'))

    async def load(self) -> None:

        configs = await self.bot.db.fetch('SELECT * FROM users')
        notifications = await self.bot.db.fetch('SELECT * FROM notifications')

        for config_data, notification_data in zip(configs, notifications):
            user_config = objects.UserConfig(data=config_data)
            user_config.notifications = objects.Notifications(data=notification_data)
            self.configs[user_config.id] = user_config

        __log__.info(f'[USER MANAGER] Loaded user configs. [{len(configs)} users]')
        print(f'[USER MANAGER] Loaded user configs. [{len(configs)} users]')

        await self.bot.reminder_manager.load()
        await self.bot.todo_manager.load()

    # Background tasks.

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

    # User management

    def get_config(self, user_id: int) -> Union[objects.DefaultUserConfig, objects.UserConfig]:
        return self.configs.get(user_id, self.default_config)

    async def create_config(self, user_id: int) -> objects.UserConfig:

        data = await self.bot.db.fetchrow('INSERT INTO users (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *', user_id)
        self.configs[user_id] = objects.UserConfig(data=data)

        __log__.info(f'[USER MANAGER] Created config for user with id \'{user_id}\'')
        return self.configs[user_id]

    async def get_or_create_config(self, user_id: int) -> objects.UserConfig:

        if isinstance(user_config := self.get_config(user_id), objects.DefaultUserConfig):
            user_config = await self.create_config(user_id)

        return user_config

    # Regular settings

    async def set_blacklisted(self, user_id: int, *, blacklisted: bool = True, reason: str = None) -> None:

        user_config = await self.get_or_create_config(user_id)

        query = 'UPDATE users SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $3 RETURNING blacklisted, blacklisted_reason'
        data = await self.bot.db.fetchrow(query, blacklisted, reason, user_id)
        user_config.blacklisted = data['blacklisted']
        user_config.blacklisted_reason = data['blacklisted_reason']

    async def set_colour(self, user_id: int, *, colour: str = str(discord.Colour.gold())) -> None:

        user_config = await self.get_or_create_config(user_id)

        data = await self.bot.db.fetchrow('UPDATE users SET colour = $1 WHERE id = $2', f'0x{colour.strip("#")}', user_id)
        user_config.colour = discord.Colour(int(data['colour'], 16))

    async def set_timezone(self, user_id: int, *, timezone: str = None, private: bool = None) -> None:

        user_config = await self.get_or_create_config(user_id)
        timezone = str(user_config.timezone) if timezone is None else timezone
        private = user_config.timezone_private if private is None else private

        data = await self.bot.db.fetchrow('UPDATE users SET timezone = $1, timezone_private = $2 WHERE id = $3 RETURNING timezone, timezone_private', timezone, private, user_id)
        user_config.timezone = pendulum.timezone(data['timezone'])
        user_config.timezone_private = private

    async def set_birthday(self,  user_id: int, *, birthday: pendulum.datetime = None, private: bool = None) -> None:

        user_config = await self.get_or_create_config(user_id)
        birthday = user_config.birthday if birthday is None else birthday
        private = user_config.timezone_private if private is None else private

        data = await self.bot.db.fetchrow('UPDATE users SET birthday = $1, birthday_private = $2 WHERE id = $3 RETURNING birthday, birthday_private', birthday, private, user_id)
        user_config.birthday = pendulum.parse(data['birthday'].isoformat(), tz='UTC')
        user_config.birthday_private = private

    # Economy stuff

    async def set_coins(self, user_id: int, *, coins: int, operation: enums.Operation = enums.Operation.ADD) -> None:

        user_config = await self.get_or_create_config(user_id)

        if operation == enums.Operation.SET:
            user_config.coins = coins
        elif operation == enums.Operation.ADD:
            user_config.coins += coins
        elif operation == enums.Operation.MINUS:
            user_config.coins -= coins

        user_config.requires_db_update.add(enums.Updateable.COINS)

    async def set_xp(self, user_id: int, *, xp: int, operation: enums.Operation = enums.Operation.ADD) -> None:

        user_config = await self.get_or_create_config(user_id)

        if operation == enums.Operation.SET:
            user_config.xp = xp
        elif operation == enums.Operation.ADD:
            user_config.xp += xp
        elif operation == enums.Operation.MINUS:
            user_config.xp -= xp

        user_config.requires_db_update.add(enums.Updateable.XP)

    async def set_bundle_collection(
            self, user_id: int, *, collection_type: Union[enums.Updateable.DAILY_COLLECTED, enums.Updateable.WEEKLY_COLLECTED, enums.Updateable.MONTHLY_COLLECTED],
            when: DateTime = pendulum.now(tz='UTC')
    ) -> None:

        user_config = await self.get_or_create_config(user_id)

        data = await self.bot.db.fetchrow(f'UPDATE users SET {collection_type.value} = $1 WHERE id = $2 RETURNING {collection_type.value}', when, user_id)
        setattr(user_config, collection_type.value, pendulum.instance(data[collection_type.value], tz='UTC'))

    async def set_bundle_streak(
            self, user_id: int, *, bundle_type: Union[enums.Updateable.DAILY_STREAK, enums.Updateable.WEEKLY_STREAK, enums.Updateable.MONTHLY_STREAK],
            operation: enums.Operation = enums.Operation.SET, count: int = 0
    ) -> None:

        user_config = await self.get_or_create_config(user_id)

        streak = None
        if operation == enums.Operation.SET:
            streak = count
        elif operation == enums.Operation.ADD:
            streak = getattr(user_config, bundle_type.value) + count
        elif operation == enums.Operation.MINUS:
            streak = getattr(user_config, bundle_type.value) - count
        elif operation == enums.Operation.RESET:
            streak = 0

        data = await self.bot.db.fetchrow(f'UPDATE users SET {bundle_type.value} = $1 WHERE id = $2 RETURNING {bundle_type.value}', streak, user_id)
        setattr(user_config, bundle_type.value, data[bundle_type.value])

    # Timecard image

    async def create_timecard(self, *, guild_id: int) -> discord.File:

        guild = self.bot.get_guild(guild_id)
        user_configs = sorted(self.configs.items(), key=lambda kv: kv[1].time.offset_hours)

        user_timezones = {}

        for user_id, user_config in user_configs:

            if not (member := guild.get_member(user_id)):
                continue
            if user_config.timezone_private or user_config.timezone == pendulum.timezone('UTC'):
                continue

            avatar_bytes = io.BytesIO(await member.avatar_url_as(format='png', size=256).read())
            time_format = user_config.time.format('HH:mm (ZZ)')

            if (users := user_timezones.get(time_format)) is None:
                user_timezones[time_format] = [avatar_bytes]
                continue

            if len(users) > 36:
                break
            user_timezones[time_format].append(avatar_bytes)

        if not user_timezones:
            raise exceptions.ArgumentError('There are no users with timezones set in this server.')

        buffer = await self.bot.loop.run_in_executor(None, self.create_timecard_image, user_timezones)
        file = discord.File(fp=buffer, filename='level.png')

        buffer.close()
        for avatar_bytes_list in user_timezones.values():
            [avatar_bytes.close() for avatar_bytes in avatar_bytes_list]

        return file

    def create_timecard_image(self, timezone_users: dict) -> io.BytesIO:

        buffer = io.BytesIO()

        width_x = (1600 * (len(timezone_users.keys()) if len(timezone_users.keys()) < 5 else 5)) + 100
        height_y = (1800 * math.ceil(len(timezone_users.keys()) / 5)) + 100

        with Image.new('RGBA', (width_x, height_y), color='#F1C30F') as image:

            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(self.ARIAL_FONT, 120)

            x = 100
            y = 100

            for timezone, avatars in timezone_users.items():

                draw.text((x, y), timezone, font=font, fill='#1B1A1C')

                user_x = x
                user_y = y + 200

                for avatar in avatars[:36]:

                    with Image.open(avatar) as avatar_image:
                        avatar_image = avatar_image.resize((250, 250))
                        image.paste(avatar_image, (user_x, user_y), avatar_image.convert('RGBA'))

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

            image.save(buffer, 'png')

        buffer.seek(0)
        return buffer

    # Ranking

    def leaderboard(self, *, guild_id: int = None, lb_type: Literal['level', 'xp', 'coins']) -> list[objects.UserConfig]:

        if not guild_id:
            configs = filter(lambda kv: self.bot.get_user(kv[1].id) is not None and getattr(kv[1], lb_type) != 0, self.configs.items())

        else:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                raise exceptions.ArgumentError('Guild with that id not found.')

            configs = filter(lambda kv: guild.get_member(kv[1].id) is not None and getattr(kv[1], lb_type) != 0, self.configs.items())

        return sorted(configs, key=lambda kv: getattr(kv[1], lb_type), reverse=True)

    def rank(self, user_id: int, *, guild_id: int = None) -> int:

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

    # Level image

    async def create_level_card(self, user_id: int, *, guild_id: int) -> discord.File:

        guild = self.bot.get_guild(guild_id)
        user = guild.get_member(user_id)
        user_config = self.get_config(user_id)

        avatar_bytes = io.BytesIO(await user.avatar_url_as(format='png', size=256).read())

        buffer = await self.bot.loop.run_in_executor(None, self.create_level_card_image, user, user_config, avatar_bytes)
        file = discord.File(fp=buffer, filename='level.png')

        buffer.close()
        avatar_bytes.close()

        return file

    def create_level_card_image(self, member: Union[discord.Member, discord.User], user_config: objects.UserConfig, avatar_bytes: io.BytesIO) -> io.BytesIO:

        buffer = io.BytesIO()
        card_image = random.choice(self.IMAGES['SAI']['level_cards'])

        with Image.open(card_image) as image:

            draw = ImageDraw.Draw(image)

            with Image.open(avatar_bytes) as avatar:

                avatar = avatar.resize((256, 256), resample=Image.LANCZOS) if avatar.size != (256, 256) else avatar
                image.paste(avatar, (22, 22), avatar.convert('RGBA'))

                colour = ColorThief(avatar_bytes).get_color(quality=1)

            # Username

            name_text = getattr(member, 'nick', None) or member.name
            name_fontsize = 56
            name_font = ImageFont.truetype(self.KABEL_BLACK_FONT, name_fontsize)

            while draw.textsize(name_text, font=name_font) > (690, 45):
                name_fontsize -= 1
                name_font = ImageFont.truetype(self.KABEL_BLACK_FONT, name_fontsize)

            draw.text((300, 22 - name_font.getoffset(name_text)[1]), name_text, font=name_font, fill=colour)

            # Level

            level_text = f'Level: {user_config.level}'
            level_font = ImageFont.truetype(self.KABEL_BLACK_FONT, 40)

            draw.text((300, 72 - level_font.getoffset(level_text)[1]), level_text, font=level_font, fill='#1F1E1C')

            # XP

            xp_text = f'XP: {user_config.xp} / {user_config.xp + user_config.next_level_xp}'
            xp_font = ImageFont.truetype(self.KABEL_BLACK_FONT, 40)

            draw.text((300, 112 - xp_font.getoffset(xp_text)[1]), xp_text, font=xp_font, fill='#1F1E1C')

            # XP BAR

            bar_len = 678
            outline = utils.darken_colour(*colour, 0.2)

            draw.rounded_rectangle(((300, 152), (300 + bar_len, 192)), radius=10, outline=outline, fill='#1F1E1C', width=5)

            if user_config.xp > 0:
                filled_len = int(round(bar_len * user_config.xp / float(user_config.xp + user_config.next_level_xp)))
                draw.rounded_rectangle(((300, 152), (300 + filled_len, 192)), radius=10, outline=outline, fill=colour, width=5)

            # Rank

            rank_text = f'#{self.rank(member.id)}'
            rank_font = ImageFont.truetype(self.KABEL_BLACK_FONT, 110)

            draw.text((300, 202 - rank_font.getoffset(rank_text)[1]), rank_text, font=rank_font, fill='#1F1E1C')

            #

            image.save(buffer, 'png')

        buffer.seek(0)
        return buffer
