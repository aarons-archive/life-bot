# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any, Optional

# Packages
import pendulum

# My stuff
from utilities import objects


if TYPE_CHECKING:
    # My stuff
    from core.bot import Life


class Todo:

    def __init__(self, bot: Life, user_config: objects.UserConfig, data: dict[str, Any]) -> None:
        self._bot = bot
        self._user_config = user_config

        self._id: int = data["id"]
        self._user_id: int = data["user_id"]
        self._created_at: pendulum.DateTime = pendulum.instance(data["created_at"], tz="UTC")
        self._content: str = data["content"]
        self._jump_url: Optional[str] = data["jump_url"]

    def __repr__(self) -> str:
        return f"<Todo id=\"{self.id}\" user_id=\"{self.user_id}\">"

    # Properties

    @property
    def bot(self) -> Life:
        return self._bot

    @property
    def user_config(self) -> objects.UserConfig:
        return self._user_config

    @property
    def id(self) -> int:
        return self._id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def created_at(self) -> pendulum.DateTime:
        return self._created_at

    @property
    def content(self) -> str:
        return self._content

    @property
    def jump_url(self) -> Optional[str]:
        return self._jump_url

    # Misc

    async def delete(self) -> None:
        await self.bot.db.execute("DELETE FROM todos WHERE id = $1", self.id)
        del self.user_config._todos[self.id]

    # Config

    async def change_content(self, content: str, *, jump_url: Optional[str] = None) -> None:
        data = await self.bot.db.fetchrow("UPDATE todos SET content = $1, jump_url = $2 WHERE id = $3 RETURNING content, jump_url", content, jump_url, self.id)
        self._content = data["content"]
        self._jump_url = data["jump_url"] or self.jump_url
