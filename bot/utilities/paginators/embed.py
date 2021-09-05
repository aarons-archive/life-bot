# Future
from __future__ import annotations

# Standard Library
from typing import Any, Optional

# Packages
import discord

# My stuff
from core import colours
from utilities import context, paginators, utils


class EmbedPaginator(paginators.BasePaginator):

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
        footer: Optional[str] = None,
        embed_footer: Optional[str] = None,
        embed_footer_url: Optional[str] = None,
        image: Optional[str] = None,
        thumbnail: Optional[str] = None,
        author: Optional[str] = None,
        author_url: Optional[str] = None,
        author_icon_url: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        colour: discord.Colour = colours.MAIN,
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

        self.embed_footer: Optional[str] = embed_footer
        self.embed_footer_url: Optional[str] = embed_footer_url

        self.embed_image: Optional[str] = image
        self.embed_thumbnail: Optional[str] = thumbnail

        self.embed_author: Optional[str] = author
        self.embed_author_url: Optional[str] = author_url
        self.embed_author_icon_url: Optional[str] = author_icon_url

        self.embed_title: Optional[str] = title
        self.embed_url: Optional[str] = url

        self.embed_colour: discord.Colour = colour

        self.embed: discord.Embed = utils.embed(
            footer=embed_footer,
            footer_url=embed_footer_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            url=url,
            colour=colour,
        )

    # Abstract methods

    async def set_page(self, *, page: int) -> None:
        self.embed.description = f"{self.CODEBLOCK_START}{self.header}{self.pages[page]}{self.footer}{self.CODEBLOCK_END}"

    async def change_page(self, *, page: int) -> None:

        await super().change_page(page=page)
        await self.message.edit(embed=self.embed, view=self.view)

    async def paginate(self) -> None:

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(embed=self.embed, view=self.view)
