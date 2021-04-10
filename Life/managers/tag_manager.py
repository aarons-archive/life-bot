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
from typing import Optional, TYPE_CHECKING

import discord
import rapidfuzz

from utilities import objects

if TYPE_CHECKING:
    from bot import Life


__log__ = logging.getLogger(__name__)


class TagManager:

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    async def load(self) -> None:

        tags = await self.bot.db.fetch('SELECT * FROM tags')
        for tag_data in tags:
            tag = objects.Tag(data=tag_data)

            guild_config = await self.bot.guild_manager.get_or_create_config(tag.guild_id)
            guild_config.tags[tag.name] = tag

        __log__.info(f'[TAG MANAGER] Loaded tags. [{len(tags)} tags]')
        print(f'[TAG MANAGER] Loaded tags. [{len(tags)} tags]')

    #

    async def get_tag(self, *, guild_id: int, name: str) -> Optional[objects.Tag]:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)
        return guild_config.tags.get(name)

    async def get_tags(self, *, guild_id: int) -> Optional[list[objects.Tag]]:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)
        return list(guild_config.tags.values())

    async def get_tags_matching(self, *, guild_id: int, name: str, limit: int = 5) -> Optional[list[objects.Tag]]:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)

        matches = [match[0] for match in rapidfuzz.process.extract(query=name, choices=list(guild_config.tags.keys()), limit=limit, processor=lambda s: s)]
        return [guild_config.tags[tag_name] for tag_name in matches]

    async def get_tags_owned_by(self, *, guild_id: int, member: discord.Member) -> Optional[list[objects.Tag]]:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)
        return [tag for tag in guild_config.tags.values() if tag.user_id == member.id]

    #

    async def create_tag(self, *, user_id: int, guild_id: int, name: str, content: str, jump_url: str = None) -> None:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)

        tag_data = await self.bot.db.fetchrow(
                'INSERT INTO tags (user_id, guild_id, name, content, jump_url) VALUES ($1, $2, $3, $4, $5) RETURNING *',
                user_id, guild_id, name, content, jump_url
        )
        guild_config.tags[tag_data['name']] = objects.Tag(data=tag_data)

    async def create_tag_alias(self, *, user_id: int, guild_id: int, alias: str, original: str, jump_url: str = None) -> None:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)

        tag_data = await self.bot.db.fetchrow(
                'INSERT INTO tags (user_id, guild_id, name, alias, jump_url) VALUES ($1, $2, $3, $4, $5) RETURNING *',
                user_id, guild_id, alias, original, jump_url
        )
        guild_config.tags[tag_data['name']] = objects.Tag(data=dict(tag_data))

    async def edit_tag_content(self, *, guild_id: int, name: str, content: str, jump_url: str = None) -> None:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)

        await self.bot.db.execute('UPDATE tags SET content = $1, jump_url = $2 WHERE name = $3 and guild_id = $4', content, jump_url, name, guild_id)
        guild_config.tags[name].content = content
        if jump_url:
            guild_config.tags[name].jump_url = jump_url

    async def edit_tag_owner(self, *, guild_id: int, name: str, user_id: int) -> None:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)

        await self.bot.db.execute('UPDATE tags SET user_id = $1 WHERE name = $2 and guild_id = $3', user_id, name, guild_id)
        guild_config.tags[name].user_id = user_id

    async def delete_tag(self, *, guild_id: int, name: str) -> None:

        guild_config = await self.bot.guild_manager.get_or_create_config(guild_id)

        await self.bot.db.execute('DELETE FROM tags WHERE name = $1 and guild_id = $2', name, guild_id)
        aliases = await self.bot.db.fetch('DELETE FROM tags WHERE alias = $1 and guild_id = $2 RETURNING name', name, guild_id)

        del guild_config.tags[name]
        for alias in aliases:
            del guild_config.tags[alias['name']]
