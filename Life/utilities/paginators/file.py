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

import functools
import io
from typing import Optional

from utilities import context, paginators, utils


class FilePaginator(paginators.BasePaginator):

    def __init__(
            self, *, ctx: context.Context, entries: list[functools.partial], timeout: int = 300, delete_message_when_done: bool = False, header: Optional[str] = None, footer: Optional[str] = None
    ) -> None:
        super().__init__(ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message_when_done=delete_message_when_done)

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

        await super().paginate()
        self.message = await self.ctx.reply(await self.generate_page(self.page), view=self.view)

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
