# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
import slate
import slate.obsidian

# My stuff
from utilities import context


if TYPE_CHECKING:

    # My stuff
    from utilities import custom


class Queue(slate.Queue[slate.obsidian.Track]):

    def __init__(
        self,
        player: custom.Player,
        /
    ) -> None:

        super().__init__()
        self.player: custom.Player = player

    def put(
        self,
        items: list[slate.obsidian.Track[context.Context]] | slate.obsidian.Track[context.Context],
        /,
        *,
        position: int | None = None
    ) -> None:

        super().put(items, position=position)

        self.player._queue_add_event.set()
        self.player._queue_add_event.clear()
