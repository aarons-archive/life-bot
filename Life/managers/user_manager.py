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




    async def set_user_config(self, *, user: typing.Union[discord.User, discord.Member], attribute: str, value: typing.Any, operation: str = 'add') -> None:

        user_config = self.get_user_config(user=user)
        if isinstance(user_config, objects.DefaultUserConfig):
            query = 'INSERT INTO user_configs (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *'
            data = await self.db.fetchrow(query, user.id)
            self.user_configs[user.id] = objects.UserConfig(data=dict(data))

        if attribute == 'colour':
            query = 'UPDATE user_configs SET colour = $1 WHERE id = $2 RETURNING *'
            data = await self.db.fetchrow(query, value, user.id)
            user_config.colour = discord.Colour(int(data['colour'], 16))

        elif attribute == 'timezone':
            query = 'UPDATE user_configs SET timezone = $1 WHERE id = $2 RETURNING *'
            data = await self.db.fetchrow(query, value, user.id)
            user_config.timezone = data['timezone']
