from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from discord.ext import tasks

from utilities import objects


if TYPE_CHECKING:
    from core.bot import Life

__log__: logging.Logger = logging.getLogger("utilities.managers.guilds")


class GuildManager:

    def __init__(self, bot: Life) -> None:
        self.bot: Life = bot

        self.cache: dict[int, objects.GuildConfig] = {}

    async def fetch_config(self, guild_id: int, *, cache: bool = True) -> objects.GuildConfig:

        data = await self.bot.db.fetchrow("INSERT INTO guilds (id) values ($1) ON CONFLICT (id) DO UPDATE SET id = excluded.id RETURNING *", guild_id)
        guild_config = objects.GuildConfig(bot=self.bot, data=data)
        __log__.info(f"[GUILDS] Fetched config for '{guild_id}'.")

        if cache:
            self.cache[guild_config.id] = guild_config
            __log__.info(f"[GUILDS] Cached config for '{guild_id}'.")

        return guild_config

    async def get_config(self, guild_id: int) -> objects.GuildConfig:

        if (guild_config := self.cache.get(guild_id)) is not None:
            __log__.debug(f"[GUILDS] Loaded config from cache for '{guild_id}'.")
            return guild_config

        __log__.debug(f"[GUILDS] Fetching config from database for '{guild_id}'.")
        return await self.fetch_config(guild_id)

    async def delete_config(self, guild_id: int) -> None:

        await self.bot.db.execute("DELETE FROM guilds WHERE id = $1", guild_id)
        try:
            del self.cache[guild_id]
        except KeyError:
            pass

        __log__.info(f"[GUILDS] Deleted config for '{guild_id}'.")

    # Background task

    @tasks.loop(seconds=60)
    async def update_database_task(self) -> None:

        async with self.bot.db.acquire(timeout=300) as db:

            requires_updating = {guild_id: guild_config for guild_id, guild_config in self.configs.items() if len(guild_config._requires_db_update) >= 1}
            for guild_id, guild_config in requires_updating.items():

                query = ",".join(f"{editable.value} = ${index + 2}" for index, editable in enumerate(guild_config._requires_db_update))
                args = [getattr(guild_config, attribute.value) for attribute in guild_config._requires_db_update]
                await db.execute(f"UPDATE users SET {query} WHERE id = $1", guild_id, *args)

                guild_config._requires_db_update = set()
