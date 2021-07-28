from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from utilities import objects


if TYPE_CHECKING:
    from core.bot import Life

__log__: logging.Logger = logging.getLogger('utilities.objects.notifications')


class Notifications:

    def __init__(self, bot: Life, user_config: objects.UserConfig, data: dict[str, Any]) -> None:
        self._bot = bot
        self._user_config = user_config

        self._id: int = data.get('id', 0)
        self._user_id: int = data.get('user_id', 0)

        self._level_ups: bool = data.get('level_ups', False)

    def __repr__(self) -> str:
        return f'<Notifications id=\'{self.id}\' user_id=\'{self.user_id}\' level_ups={self.level_ups}>'

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
    def level_ups(self) -> bool:
        return self._level_ups
