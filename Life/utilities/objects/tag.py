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

import pendulum
from pendulum import DateTime

from utilities import objects

if TYPE_CHECKING:
    from bot import Life


__log__ = logging.getLogger('utilities.objects.tag')


class Tag:

    __slots__ = '_bot', '_guild_config', '_id', '_user_id', '_guild_id', '_created_at', '_name', '_alias', '_content', '_jump_url'

    def __init__(self, bot: Life, guild_config: objects.GuildConfig, data: dict) -> None:

        self._bot = bot
        self._guild_config = guild_config

        self._id: int = data.get('id')
        self._user_id: int = data.get('user_id')
        self._guild_id: int = data.get('guild_id')
        self._created_at: DateTime = pendulum.instance(data.get('created_at'), tz='UTC')
        self._name: str = data.get('name')
        self._alias: Optional[str] = data.get('alias')
        self._content: Optional[str] = data.get('content')
        self._jump_url: Optional[str] = data.get('jump_url')

    def __repr__(self) -> str:
        return f'<Tag id=\'{self.id}\' user_id=\'{self.user_id}\' guild_id=\'{self.guild_id}\' name=\'{self.name}\' alias=\'{self.alias}\'>'

    # Properties

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
    def created_at(self) -> DateTime:
        return self._created_at

    @property
    def name(self) -> str:
        return self._name

    @property
    def alias(self) -> Optional[str]:
        return self._alias

    @property
    def content(self) -> Optional[str]:
        return self._content

    @property
    def jump_url(self) -> Optional[str]:
        return self._jump_url

    #
