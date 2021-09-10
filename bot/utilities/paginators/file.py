# Future
from __future__ import annotations

# Standard Library
import functools

# My stuff
from utilities import context, paginators, utils


class FilePaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: context.Context,
        entries: list[functools.partial],
        timeout: int = 300,
        delete_message: bool = False,
        header: str | None = None,
    ) -> None:

        super().__init__(ctx=ctx, entries=entries, per_page=1, timeout=timeout, delete_message=delete_message)

        self.header: str = header or ""

        self.current_page: str | None = None

    # Abstract methods

    async def set_page(self, *, page: int) -> None:

        buffer = await self.entries[page]()
        url = await utils.upload_file(self.ctx.bot.session, file_bytes=buffer, file_format="png")
        buffer.close()

        self.current_page = f"{self.header}{url}"

    async def change_page(self, *, page: int) -> None:

        await super().change_page(page=page)
        await self.message.edit(content=self.current_page, view=self.view)

    async def paginate(self) -> None:

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(content=self.current_page, view=self.view)
