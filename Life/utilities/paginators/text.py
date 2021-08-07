from __future__ import annotations

from typing import Any, Optional

from core import values
from utilities import context, paginators


class TextPaginator(paginators.BasePaginator):

    def __init__(
            self, *, ctx: context.Context, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = "\n",
            header: Optional[str] = None, footer: Optional[str] = None
    ) -> None:
        super().__init__(ctx=ctx, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter)

        self._header: Optional[str] = header
        self._footer: Optional[str] = footer

    # Properties

    @property
    def header(self) -> str:
        return self._header or ""

    @property
    def footer(self) -> str:
        return self._footer or f"\n\nPage: {self.page + 1}/{len(self.pages)} | Total entries: {len(self.entries)}"

    # Abstract methods

    async def set_page(self, *, page: int) -> None:

        self.current_page = f"{f'```{values.NL}' if self.codeblock else ''}{self.header}{self.pages[page]}{self.footer}{f'{values.NL}```' if self.codeblock else ''}"

    async def change_page(self, *, page: int) -> None:

        self.page = page
        await self.set_page(page=page)

        await self.message.edit(content=self.current_page)

    async def paginate(self) -> None:

        await super().paginate()

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(self.current_page, view=self.view)
