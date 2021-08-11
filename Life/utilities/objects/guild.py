from __future__ import annotations

import logging
from typing import Any, Optional, TYPE_CHECKING

import pendulum
import rapidfuzz

from utilities import enums, objects


if TYPE_CHECKING:
    from core.bot import Life

__log__: logging.Logger = logging.getLogger("utilities.objects.guild")


class GuildConfig:

    def __init__(self, bot: Life, data: dict[str, Any]) -> None:
        self._bot = bot

        self._id: int = data["id"]
        self._created_at: pendulum.DateTime = pendulum.instance(data["created_at"], tz="UTC")

        self._embed_size: enums.EmbedSize = enums.EmbedSize(data["embed_size"])
        self._prefixes: list[str] = data["prefixes"]

        self._tags: dict[str, objects.Tag] = {}

    def __repr__(self) -> str:
        return f"<GuildConfig id={self.id}>"

    # Properties

    @property
    def bot(self) -> Life:
        return self._bot

    @property
    def id(self) -> int:
        return self._id

    @property
    def created_at(self) -> pendulum.DateTime:
        return self._created_at

    @property
    def embed_size(self) -> enums.EmbedSize:
        return self._embed_size

    @property
    def prefixes(self) -> list[str]:
        return self._prefixes

    #

    @property
    def tags(self) -> dict[str, objects.Tag]:
        return self._tags

    # Config

    async def set_embed_size(self, embed_size: enums.EmbedSize) -> None:

        data = await self.bot.db.fetchrow("UPDATE guilds SET embed_size = $1 WHERE id = $2 RETURNING embed_size", embed_size.value, self.id)
        self._embed_size = enums.EmbedSize(data["embed_size"])

    async def change_prefixes(self, prefix: Optional[str] = None, *, operation: enums.Operation) -> None:

        if operation == enums.Operation.RESET:
            data = await self.bot.db.fetchrow("UPDATE guilds SET prefixes = $1 WHERE id = $2 RETURNING prefixes", [], self.id)
        elif operation == enums.Operation.ADD:
            data = await self.bot.db.fetchrow("UPDATE guilds SET prefixes = array_append(prefixes, $1) WHERE id = $2 RETURNING prefixes", prefix, self.id)
        elif operation == enums.Operation.REMOVE:
            data = await self.bot.db.fetchrow("UPDATE guilds SET prefixes = array_remove(prefixes, $1) WHERE id = $2 RETURNING prefixes", prefix, self.id)
        else:
            raise ValueError(f"'change_prefixes' expected one of {enums.Operation.ADD, enums.Operation.REMOVE, enums.Operation.RESET}, got '{operation!r}'.")

        self._prefixes = data["prefixes"]

    # Caching

    async def fetch_tags(self) -> None:

        if not (tags := await self.bot.db.fetch("SELECT * FROM tags WHERE guild_id = $1", self.id)):
            return

        for tag_data in tags:
            tag = objects.Tag(bot=self.bot, guild_config=self, data=tag_data)
            self._tags[tag.name] = tag

        __log__.debug(f"[GUILDS] Fetched and cached tags ({len(tags)}) for '{self.id}'.")

    # Tags

    async def create_tag(self, *, user_id: int, name: str, content: str, jump_url: Optional[str] = None) -> objects.Tag:

        data = await self.bot.db.fetchrow(
            "INSERT INTO tags (user_id, guild_id, name, content, jump_url) VALUES ($1, $2, $3, $4, $5) RETURNING *",
            user_id, self.id, name, content, jump_url
        )

        tag = objects.Tag(bot=self.bot, guild_config=self, data=data)
        self._tags[tag.name] = tag

        return tag

    async def create_tag_alias(self, *, user_id: int, name: str, original: int, jump_url: Optional[str] = None) -> objects.Tag:

        data = await self.bot.db.fetchrow(
            "INSERT INTO tags (user_id, guild_id, name, alias, jump_url) VALUES ($1, $2, $3, $4, $5) RETURNING *",
            user_id, self.id, name, original, jump_url
        )

        tag = objects.Tag(bot=self.bot, guild_config=self, data=data)
        self._tags[tag.name] = tag

        return tag

    def get_tag(self, *, tag_name: Optional[str] = None, tag_id: Optional[int] = None) -> Optional[objects.Tag]:

        if tag_name:
            tag = self.tags.get(tag_name)

        elif tag_id:
            if not (tags := [tag for tag in self.tags.values() if tag.id == tag_id]):
                return None
            tag = tags[0]

        else:
            raise ValueError("\"tag_name\" or \"tag_id\" parameter must be specified.")

        return tag

    def get_all_tags(self) -> Optional[list[objects.Tag]]:
        return list(self.tags.values())

    def get_user_tags(self, user_id: int) -> Optional[list[objects.Tag]]:
        return [tag for tag in self.tags.values() if tag.user_id == user_id]

    def get_tags_matching(self, name: str, *, limit: int = 5) -> Optional[list[objects.Tag]]:
        return [self.get_tag(tag_name=match) for match, _, _ in rapidfuzz.process.extract(query=name, choices=list(self.tags.keys()), processor=lambda t: t, limit=limit)]

    async def delete_tag(self, *, tag_name: Optional[str] = None, tag_id: Optional[int] = None) -> None:

        if not tag_name or not tag_id:
            raise ValueError("\"tag_name\" or \"tag_id\" parameter must be specified.")

        if not (tag := self.get_tag(tag_name=tag_name, tag_id=tag_id)):
            return

        await tag.delete()
