# Future
from __future__ import annotations

# Standard Library
from typing import Any

# Packages
import discord

# My stuff
from utilities import custom, paginators


class EmbedsPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: custom.Context,
        entries: list[Any],
        timeout: int = 300,
        delete_message: bool = False,
    ) -> None:

        super().__init__(ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message=delete_message, join_pages=False)

        self.current_page: discord.Embed | None = None

    # Abstract methods

    async def set_page(self, *, page: int) -> None:
        self.current_page = self.pages[page]

    async def change_page(self, *, page: int) -> None:

        await super().change_page(page=page)
        await self.message.edit(embed=self.current_page, view=self.view)

    async def paginate(self) -> None:

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(embed=self.current_page, view=self.view)
