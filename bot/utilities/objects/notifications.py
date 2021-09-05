# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING, Any

# My stuff
from utilities import objects


if TYPE_CHECKING:
    # My stuff
    from core.bot import Life


class Notifications:

    def __init__(self, bot: Life, user_config: objects.UserConfig, data: dict[str, Any]) -> None:
        self._bot = bot
        self._user_config = user_config

        self._id: int = data["id"]
        self._user_id: int = data["user_id"]

        self._level_ups: bool = data["level_ups"]

    def __repr__(self) -> str:
        return f"<Notifications id={self.id} user_id={self.user_id} level_ups={self.level_ups}>"

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

    # Notifications

    @property
    def level_ups(self) -> bool:
        return self._level_ups
