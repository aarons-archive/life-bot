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


from __future__ import annotations

from typing import TYPE_CHECKING

import slate


if TYPE_CHECKING:
    from typing import Any, Union
    from cogs.voice.custom.player import Player


class Queue(slate.Queue):

    def __init__(self, player: Player) -> None:
        super().__init__()

        self.player: Player = player

    def put(self, *, items: Union[list[Any], Any], position: int = None) -> None:
        super().put(items=items, position=position)

        self.player.queue_add_event.set()
        self.player.queue_add_event.clear()
