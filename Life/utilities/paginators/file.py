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
from typing import Optional

from utilities import context, paginators, utils


class FilePaginator(paginators.BasePaginator):

    def __init__(
            self, *, ctx: context.Context, entries: list[functools.partial], timeout: int = 300, delete_message: bool = True, header: Optional[str] = None
    ) -> None:
        super().__init__(ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message=delete_message)

        self._header: Optional[str] = header

        self.current_page: Optional[str] = None

    # Properties

    @property
    def header(self) -> str:
        return self._header or f"\n\nPage: {self.page + 1}/{len(self.entries)} | Total entries: {len(self.entries)}\n"

    # Abstract methods

    async def set_page(self, *, page: int) -> None:

        buffer = await self.entries[page](page=page)
        url = await utils.upload_image(session=self.ctx.bot.session, buffer=buffer)
        buffer.close()

        self.current_page = f"{self.header}{url}"

    async def change_page(self, *, page: int) -> None:

        self.page = page
        await self.set_page(page=page)

        await self.message.edit(content=self.current_page)

    async def paginate(self) -> None:

        await super().paginate()

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(self.current_page, view=self.view)
