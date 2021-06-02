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

from typing import Optional, TYPE_CHECKING

import discord

from utilities import context, paginators


if TYPE_CHECKING:
    from bot import Life


class EmbedsPaginator(paginators.BasePaginator):

    __slots__ = 'bot', 'ctx', 'entries', 'per_page', 'timeout', 'delete_messages_when_done', 'delete_reactions_when_done', 'codeblock', 'splitter', 'reaction_event', 'task', 'message', 'looping', \
                'page', 'BUTTONS', '_content'

    def __init__(
            self, *, bot: Life = None, ctx: context.Context, entries: list[discord.Embed], timeout: int = 300, delete_message_when_done: bool = False, delete_reactions_when_done: bool = True,
            content: Optional[str] = None
    ) -> None:
        super().__init__(
                bot=bot, ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message_when_done=delete_message_when_done, delete_reactions_when_done=delete_reactions_when_done,
        )

        self._content: Optional[str] = content

    # Properties

    @property
    def content(self) -> str:
        return self._content or f'\n\nPage: {self.page + 1}/{len(self.entries)} | Total entries: {len(self.entries)}\n'

    # Page generator

    async def generate_page(self, page: int = 0) -> dict:
        return {'content': self.content, 'embed': self.pages[page]}

    # Abstract methods

    async def paginate(self) -> None:

        self.message = await self.ctx.reply(**await self.generate_page(self.page))
        await super().paginate()

    async def first(self) -> None:

        await super().first()
        await self.message.edit(**await self.generate_page(self.page))

    async def backward(self) -> None:

        await super().backward()
        await self.message.edit(**await self.generate_page(self.page))

    async def forward(self) -> None:

        await super().forward()
        await self.message.edit(**await self.generate_page(self.page))

    async def last(self) -> None:

        await super().last()
        await self.message.edit(**await self.generate_page(self.page))
