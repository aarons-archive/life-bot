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

import logging
from typing import TYPE_CHECKING, Union

import discord

from utilities import enums, objects

if TYPE_CHECKING:
    from bot import Life


__log__ = logging.getLogger(__name__)


class GuildManager:

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.default_config = objects.DefaultGuildConfig()
        self.configs = {}

    async def load(self) -> None:

        configs = await self.bot.db.fetch('SELECT * FROM guilds')
        for config in configs:
            self.configs[config['id']] = objects.GuildConfig(data=config)

        __log__.info(f'[GUILD MANAGER] Loaded guild configs. [{len(configs)} guilds]')
        print(f'[GUILD MANAGER] Loaded guild configs. [{len(configs)} guilds]')

        await self.bot.tag_manager.load()

    # Guild management

    def get_config(self, guild_id: int) -> Union[objects.DefaultGuildConfig, objects.GuildConfig]:
        return self.configs.get(guild_id, self.default_config)

    async def create_config(self, guild_id: int) -> objects.GuildConfig:

        data = await self.bot.db.fetchrow('INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *', guild_id)
        self.configs[guild_id] = objects.GuildConfig(data=data)

        __log__.info(f'[GUILD MANAGER] Created config for guild with id \'{guild_id}\'')
        return self.configs[guild_id]

    async def get_or_create_config(self, guild_id: int) -> objects.GuildConfig:

        if isinstance(guild_config := self.get_config(guild_id), objects.DefaultGuildConfig):
            guild_config = await self.create_config(guild_id)

        return guild_config

    # Regular settings

    async def set_blacklisted(self, guild_id: int, *, blacklisted: bool = True, reason: str = None) -> None:

        guild_config = await self.get_or_create_config(guild_id)

        query = 'UPDATE guilds SET blacklisted = $1, blacklisted_reason = $2 WHERE id = $3 RETURNING blacklisted, blacklisted_reason'
        data = await self.bot.db.fetchrow(query, blacklisted, reason, guild_id)
        guild_config.blacklisted = data['blacklisted']
        guild_config.blacklisted_reason = data['blacklisted_reason']

    async def set_colour(self, guild_id: int, *, colour: str = str(discord.Colour.gold())) -> None:

        guild_config = await self.get_or_create_config(guild_id)

        data = await self.bot.db.fetchrow('UPDATE guilds SET colour = $1 WHERE id = $2 RETURNING colour', f'0x{colour.strip("#")}', guild_id)
        guild_config.colour = discord.Colour(int(data['colour'], 16))

    async def set_embed_size(self, guild_id: int, *, embed_size: enums.EmbedSize = enums.EmbedSize.LARGE) -> None:

        guild_config = await self.get_or_create_config(guild_id)

        data = await self.bot.db.fetchrow('UPDATE guilds SET embed_size = $1 WHERE id = $2 RETURNING embed_size', embed_size.value, guild_id)
        # noinspection PyArgumentList
        guild_config.embed_size = enums.EmbedSize(data['embed_size'])

    async def set_prefixes(self, guild_id: int, *, operation: enums.Operation = enums.Operation.ADD, prefix: str = None) -> None:

        guild_config = await self.get_or_create_config(guild_id)

        if operation in [enums.Operation.ADD, enums.Operation.REMOVE]:
            op = 'array_append' if operation == enums.Operation.ADD else 'array_remove'
            data = await self.bot.db.fetchrow(f'UPDATE guilds SET prefixes = {op}(prefixes, $1) WHERE id = $2 RETURNING prefixes', prefix, guild_id)
        elif operation == enums.Operation.RESET:
            data = await self.bot.db.fetchrow('UPDATE guilds SET prefixes = $1 WHERE id = $2 RETURNING prefixes', [], guild_id)
        else:
            raise ValueError('Invalid operation for editing prefixes.')

        guild_config.prefixes = data['prefixes']
