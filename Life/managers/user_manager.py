"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import typing

import discord

from utilities import objects


class UserConfigManager:

    def __init__(self, bot) -> None:
        self.bot = bot

        self.default_user_config = objects.DefaultUserConfig()
        self.configs = {}

    async def load(self) -> None:

        user_configs = await self.bot.db.fetch('SELECT * FROM user_configs')
        for user_config in user_configs:
            self.configs[user_config['id']] = objects.UserConfig(data=dict(user_config))

        print(f'[POSTGRESQL] Loaded user configs. [{len(user_configs)} users(s)]')

    def get_user_config(self, *, user_id: int) -> typing.Union[objects.DefaultUserConfig, objects.UserConfig]:
        return self.configs.get(user_id, self.default_user_config)

    async def create_user_config(self, *, user_id: int) -> objects.UserConfig:

        data = await self.bot.db.fetchrow('INSERT INTO user_configs (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *', user_id)
        self.configs[user_id] = objects.UserConfig(data=dict(data))

        return self.get_user_config(user_id=user_id)

    async def edit_user_config(self, *, user_id: int, attribute: str, value: typing.Any = None, operation: str = 'set') -> objects.UserConfig:

        user_config = self.get_user_config(user_id=user_id)
        if isinstance(user_config, objects.DefaultUserConfig):
            user_config = await self.create_user_config(user_id=user_id)

        if attribute == 'colour':
            data = await self.bot.db.fetchrow('UPDATE user_configs SET colour = $1 WHERE id = $2 RETURNING colour', value, user_id)
            user_config.colour = discord.Colour(int(data['colour'], 16))

        elif attribute == 'timezone':
            data = await self.bot.db.fetchrow('UPDATE user_configs SET timezone = $1 WHERE id = $2 RETURNING timezone', value, user_id)
            user_config.timezone = data['timezone']

        elif attribute == 'timezone_private':
            data = await self.bot.db.fetchrow('UPDATE user_configs SET timezone_private = $1 WHERE id = $2 RETURNING timezone_private', value, user_id)
            user_config.timezone_private = data['timezone_private']

        elif attribute == 'blacklist':

            if operation == 'set':
                query = 'UPDATE user_configs SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $3 RETURNING blacklisted, blacklisted_reason'
                data = await self.bot.db.fetchrow(query, True, value, user_id)
            else:
                query = 'UPDATE user_configs SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $3 RETURNING blacklisted, blacklisted_reason'
                data = await self.bot.db.fetchrow(query, False, 'None', user_id)

            user_config.blacklisted = data['blacklisted']
            user_config.blacklisted_reason = data['blacklisted_reason']

        return user_config
