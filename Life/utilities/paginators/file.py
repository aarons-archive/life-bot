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

import functools
from typing import Optional, TYPE_CHECKING

from utilities import context, paginators, utils

if TYPE_CHECKING:
    from bot import Life


class FilePaginator(paginators.BasePaginator):

    __slots__ = 'bot', 'ctx', 'entries', 'per_page', 'timeout', 'delete_messages_when_done', 'delete_reactions_when_done', 'codeblock', 'splitter', 'reaction_event', 'task', 'message', 'looping', \
                'page', 'BUTTONS', '_header', '_footer'

    def __init__(
            self, *, bot: Life = None, ctx: context.Context, entries: list[functools.partial], timeout: int = 300, delete_message_when_done: bool = False, delete_reactions_when_done: bool = True,
            header: Optional[str] = None, footer: Optional[str] = None
    ) -> None:
        super().__init__(
                bot=bot, ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message_when_done=delete_message_when_done, delete_reactions_when_done=delete_reactions_when_done,
        )

        self._header: Optional[str] = header
        self._footer: Optional[str] = footer

    # Properties

    @property
    def header(self) -> str:
        return self._header or f'\n\nPage: {self.page + 1}/{len(self.entries)} | Total entries: {len(self.entries)}\n'

    @property
    def footer(self) -> str:
        return self._footer or ''

    # Page generator

    async def generate_page(self, page: int = 0) -> str:

        file = await self.entries[page](page=page)
        image = await utils.upload_image(bot=self.bot, file=file)

        return f'{self.header}{image}{self.footer}'

    # Abstract methods

    async def paginate(self) -> None:

        self.message = await self.ctx.reply(await self.generate_page(self.page))
        await super().paginate()

    async def first(self) -> None:

        await super().first()
        await self.message.edit(content=await self.generate_page(self.page))

    async def backward(self) -> None:

        await super().backward()
        await self.message.edit(content=await self.generate_page(self.page))

    async def forward(self) -> None:

        await super().forward()
        await self.message.edit(content=await self.generate_page(self.page))

    async def last(self) -> None:

        await super().last()
        await self.message.edit(content=await self.generate_page(self.page))
