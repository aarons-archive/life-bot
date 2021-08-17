from __future__ import annotations

from typing import Any, Optional

import discord

from utilities import context, paginators


class EmbedsPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: context.Context,
        entries: list[Any],
        timeout: int = 300,
        delete_message: bool = True,
        content: Optional[str] = None
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=1,
            timeout=timeout,
            delete_message=delete_message
        )

        self._content: Optional[str] = content

        self.current_page: Optional[discord.Embed] = None

    # Properties

    @property
    def content(self) -> str:
        return self._content or f"Page: {self.page + 1}/{len(self.entries)} | Total entries: {len(self.entries)}"

    # Abstract methods

    async def set_page(self, *, page: int) -> None:
        self.current_page = self.pages[page]

    async def change_page(self, *, page: int) -> None:

        await super().change_page(page=page)
        await self.message.edit(content=self.content, embed=self.current_page, view=self.view)

    async def paginate(self) -> None:

        await super().paginate()

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(content=self.content, embed=self.current_page, view=self.view)
