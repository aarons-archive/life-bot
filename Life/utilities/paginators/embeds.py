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

    def __init__(
            self, *, ctx: context.Context, entries: list[Any], timeout: int = 300, delete_message: bool = True, content: Optional[str] = None
    ) -> None:
        super().__init__(ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message=delete_message)

        self._content: Optional[str] = content

        self.current_page: Optional[discord.Embed] = None

    # Properties

    @property
    def content(self) -> str:
        return self._content or f'Page: {self.page + 1}/{len(self.entries)} | Total entries: {len(self.entries)}'

    # Abstract methods

    async def set_page(self, *, page: int) -> None:

        self.current_page = self.pages[page]

    async def change_page(self, *, page: int) -> None:

        self.page = page
        await self.set_page(page=page)

        await self.message.edit(embed=self.current_page)

    async def paginate(self) -> None:

        await super().paginate()

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(content=self.content, embed=self.current_page, view=self.view)
