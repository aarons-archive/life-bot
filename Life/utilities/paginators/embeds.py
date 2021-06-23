"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from typing import Any, Optional

import discord

from utilities import context, paginators


class EmbedsPaginator(paginators.BasePaginator):

    def __init__(self, *, ctx: context.Context, entries: list[discord.Embed], timeout: int = 300, delete_message_when_done: bool = False, content: Optional[str] = None) -> None:
        super().__init__(ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message_when_done=delete_message_when_done)

        self._content: Optional[str] = content

    # Properties

    @property
    def content(self) -> str:
        return self._content or f'\n\nPage: {self.page + 1}/{len(self.entries)} | Total entries: {len(self.entries)}\n'

    # Page generator

    async def generate_page(self, page: int = 0) -> dict[str, Any]:
        return {'content': self.content, 'embed': self.pages[page]}

    # Abstract methods

    async def paginate(self) -> None:
        await super().paginate()
        self.message = await self.ctx.reply(**await self.generate_page(self.page), view=self.view)

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
