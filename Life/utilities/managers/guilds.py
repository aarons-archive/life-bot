from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from utilities import objects


if TYPE_CHECKING:
    from core.bot import Life

__log__: logging.Logger = logging.getLogger("utilities.managers.guilds")


class GuildManager:

    def __init__(self, bot: Life) -> None:
        self.bot: Life = bot

        self.cache: dict[int, objects.GuildConfig] = {}

    async def fetch_config(self, guild_id: int) -> objects.GuildConfig:

        data = await self.bot.db.fetchrow("INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *", guild_id)
        guild_config = objects.GuildConfig(bot=self.bot, data=data)

        await guild_config.fetch_tags()

        self.cache[guild_config.id] = guild_config

        __log__.debug(f"[GUILDS] Cached config for '{guild_id}'.")
        return guild_config

    async def get_config(self, guild_id: int) -> objects.GuildConfig:

        if (guild_config := self.cache.get(guild_id)) is not None:
            return guild_config

        return await self.fetch_config(guild_id)

    async def delete_config(self, guild_id: int) -> None:

        await self.bot.db.execute("DELETE FROM guilds WHERE id = $1", guild_id)
        try:
            del self.cache[guild_id]
        except KeyError:
            pass

        __log__.info(f"[GUILDS] Deleted config for '{guild_id}'.")
