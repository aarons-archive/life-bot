from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

import pendulum

from utilities import objects


if TYPE_CHECKING:
    from core.bot import Life


class Tag:

    def __init__(self, bot: Life, guild_config: objects.GuildConfig, data: dict[str, Any]) -> None:

        self._bot = bot
        self._guild_config = guild_config

        self._id: int = data["id"]
        self._user_id: int = data["user_id"]
        self._guild_id: int = data["guild_id"]
        self._created_at: pendulum.DateTime = pendulum.instance(data["created_at"], tz="UTC")
        self._name: str = data["name"]
        self._alias: Optional[int] = data["alias"]
        self._content: Optional[str] = data["content"]
        self._jump_url: Optional[str] = data["jump_url"]

    def __repr__(self) -> str:
        return f"<Tag id=\"{self.id}\" user_id=\"{self.user_id}\" guild_id=\"{self.guild_id}\" name=\"{self.name}\" alias=\"{self.alias}\">"

    # Properties

    @property
    def bot(self) -> Life:
        return self._bot

    @property
    def guild_config(self) -> objects.GuildConfig:
        return self._guild_config

    @property
    def id(self) -> int:
        return self._id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def guild_id(self) -> int:
        return self._guild_id

    @property
    def created_at(self) -> pendulum.DateTime:
        return self._created_at

    @property
    def name(self) -> str:
        return self._name

    @property
    def alias(self) -> Optional[int]:
        return self._alias

    @property
    def content(self) -> Optional[str]:
        return self._content

    @property
    def jump_url(self) -> Optional[str]:
        return self._jump_url

    # Misc

    async def delete(self) -> None:

        tags = await self.bot.db.fetch("DELETE FROM tags WHERE id = $1 or alias = $1 RETURNING name", self.id)
        for tag in tags:
            del self.guild_config.tags[tag["name"]]

    # Config

    async def change_content(self, content: str, *, jump_url: Optional[str] = None) -> None:

        data = await self.bot.db.fetchrow("UPDATE tags SET content = $1, jump_url = $2 WHERE id = $3 RETURNING content, jump_url", content, jump_url, self.id)
        self._content = data["content"]
        self._jump_url = data["jump_url"] or self.jump_url

    async def change_owner(self, user_id: int) -> None:

        data = await self.bot.db.fetchrow("UPDATE tags SET user_id = $1 WHERE id = $2 RETURNING user_id", user_id, self.id)
        self._user_id = data["user_id"]
