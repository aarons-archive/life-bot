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


class GuildConfigManager:

    def __init__(self, bot) -> None:
        self.bot = bot

        self.default_guild_config = objects.DefaultGuildConfig()
        self.configs = {}

    async def load(self) -> None:

        guild_configs = await self.bot.db.fetch('SELECT * FROM guild_configs')
        for guild_config in guild_configs:
            self.configs[guild_config['id']] = objects.GuildConfig(data=dict(guild_config))

        print(f'[POSTGRESQL] Loaded guild configs. [{len(guild_configs)} guild(s)]')

    def get_guild_config(self, *, guild_id: int) -> typing.Union[objects.DefaultGuildConfig, objects.GuildConfig]:
        return self.configs.get(guild_id, self.default_guild_config)



    async def set_guild_config(self, *, guild: discord.Guild, attribute: str, value: typing.Any, operation: str = 'add') -> None:

        guild_config = self.get_guild_config(guild=guild)
        if isinstance(guild_config, objects.DefaultGuildConfig):
            query = 'INSERT INTO guild_configs (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *'
            data = await self.db.fetchrow(query, guild.id)
            self.guild_configs[guild.id] = objects.GuildConfig(data=dict(data))

        if attribute == 'prefix':
            query = 'UPDATE guild_configs SET prefixes = array_append(prefixes, $1) WHERE id = $2 RETURNING prefixes'
            if operation == 'remove':
                query = 'UPDATE guild_configs SET prefixes = array_remove(prefixes, $1) WHERE id = $2 RETURNING prefixes'
            if operation == 'clear':
                query = 'UPDATE guild_configs SET prefixes = $1 WHERE id = $2 RETURNING prefixes'

            data = await self.db.fetchrow(query, value, guild.id)
            guild_config.prefixes = data['prefixes']

        elif attribute == 'colour':
            query = 'UPDATE guild_configs SET colour = $1 WHERE id = $2 RETURNING *'
            data = await self.db.fetchrow(query, value, guild.id)
            guild_config.colour = discord.Colour(int(data['colour'], 16))
