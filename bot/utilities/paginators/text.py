from __future__ import annotations

from typing import Any, Optional

from utilities import context, paginators


class TextPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: context.Context,
        entries: list[Any],
        per_page: int,
        timeout: int = 300,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> None:

        super().__init__(
            ctx=ctx,
            entries=entries,
            per_page=per_page,
            timeout=timeout,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter
        )

        self.header: str = header or ""
        self.footer: str = footer or ""

        self.current_page: Optional[str] = None

    # Abstract methods

    async def set_page(self, *, page: int) -> None:
        self.current_page = f"{self.CODEBLOCK_START}{self.header}{self.pages[page]}{self.footer}{self.CODEBLOCK_END}"

    async def change_page(self, *, page: int) -> None:

        await super().change_page(page=page)
        await self.message.edit(content=self.current_page, view=self.view)

    async def paginate(self) -> None:

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(content=self.current_page, view=self.view)
