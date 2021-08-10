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

        buffer = await self.entries[page]()
        url = await utils.upload_file(self.ctx.bot.session, file_bytes=buffer, file_format="png")
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
