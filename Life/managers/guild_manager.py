"""
Life
Copyright (C) 2020 Axel#3456

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import typing

import discord

from utilities import objects
from utilities.enums import Editables, Operations


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

    async def create_guild_config(self, *, guild_id: int) -> objects.GuildConfig:

        data = await self.bot.db.fetchrow('INSERT INTO guild_configs (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *', guild_id)
        self.configs[guild_id] = objects.GuildConfig(data=dict(data))

        return self.configs[guild_id]

    def get_guild_config(self, *, guild_id: int) -> typing.Union[objects.DefaultGuildConfig, objects.GuildConfig]:
        return self.configs.get(guild_id, self.default_guild_config)

    async def edit_guild_config(self, *, guild_id: int, editable: Editables, operation: Operations, value: typing.Any = None) -> objects.GuildConfig:

        guild_config = self.get_guild_config(guild_id=guild_id)
        if isinstance(guild_config, objects.DefaultGuildConfig):
            guild_config = await self.create_guild_config(guild_id=guild_id)

        if editable == Editables.colour:

            operations = {
                Operations.set.value: ('UPDATE guild_configs SET colour = $1 WHERE id = $2 RETURNING colour', f'0x{str(value).strip("#")}', guild_id),
                Operations.reset.value: ('UPDATE guild_configs SET colour = $1 WHERE id = $2 RETURNING colour', f'0x{str(discord.Colour.gold()).strip("#")}', guild_id),
            }

            data = await self.bot.db.fetchrow(*operations[operation.value])
            guild_config.colour = discord.Colour(int(data['colour'], 16))

        elif editable == Editables.prefixes:

            operations = {
                Operations.add.value: ('UPDATE guild_configs SET prefixes = array_append(prefixes, $1) WHERE id = $2 RETURNING prefixes', value, guild_id),
                Operations.remove.value: ('UPDATE guild_configs SET prefixes = array_remove(prefixes, $1) WHERE id = $2 RETURNING prefixes', value, guild_id),
                Operations.reset.value: ('UPDATE guild_configs SET prefixes = $1 WHERE id = $2 RETURNING prefixes', [], guild_id)
            }

            data = await self.bot.db.fetchrow(*operations[operation.value])
            guild_config.prefixes = data['prefixes']

        elif editable == Editables.blacklist:

            operations = {
                Operations.set.value:
                    ('UPDATE guild_configs SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $2 RETURNING blacklisted, blacklisted_reason', True, value, guild_id),
                Operations.reset.value:
                    ('UPDATE guild_configs SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $2 RETURNING blacklisted, blacklisted_reason', False, None, guild_id)
            }

            data = await self.bot.db.fetchrow(*operations[operation.value])
            guild_config.blacklisted = data['blacklisted']
            guild_config.blacklisted_reason = data['blacklisted_reason']

        return guild_config
