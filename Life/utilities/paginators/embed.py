from __future__ import annotations

from typing import Any, Optional

import discord

from core import colours, values
from utilities import context, paginators


class EmbedPaginator(paginators.BasePaginator):

    def __init__(
        self,
        *,
        ctx: context.Context,
        entries: list[Any],
        per_page: int,
        timeout: int = 300,
        delete_message: bool = True,
        codeblock: bool = False,
        splitter: str = "\n",
        header: Optional[str] = None,
        footer: Optional[str] = None,
        embed_footer_url: Optional[str] = None,
        embed_footer: Optional[str] = None,
        image: Optional[str] = None,
        thumbnail: Optional[str] = None,
        author: Optional[str] = None,
        author_url: Optional[str] = None,
        author_icon_url: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        colour: discord.Colour = colours.MAIN,
        additional_footer: Optional[str] = None
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

        self.additional_footer = additional_footer

        self.embed: discord.Embed = discord.Embed(colour=self.embed_colour)

        if self._embed_footer:
            self.embed.set_footer(text=self._embed_footer, icon_url=self.embed_footer_url or discord.embeds.EmptyEmbed)

        if self.embed_image:
            self.embed.set_image(url=self.embed_image)
        if self.embed_thumbnail:
            self.embed.set_thumbnail(url=self.embed_thumbnail)

        if self.embed_author:
            self.embed.set_author(name=self.embed_author, url=self.embed_author_url or discord.embeds.EmptyEmbed, icon_url=self.embed_author_icon_url or discord.embeds.EmptyEmbed)

        if self.embed_title:
            self.embed.title = self.embed_title
        if self.embed_url:
            self.embed.url = self.embed_url

    #

    @property
    def _embed_footer(self) -> Optional[str]:
        return (self.embed_footer or f"Page: {self.page + 1}/{len(self.pages)} | Total entries: {len(self.entries)}"
                                     f"{f' | {self.additional_footer}' if self.additional_footer else ''}") if len(self.pages) != 1 else None

    # Abstract methods

    async def set_page(self, *, page: int) -> None:

        self.embed.description = f"{f'```{values.NL}' if self.codeblock else ''}{self.header}{self.pages[page]}{self.footer}{f'{values.NL}```' if self.codeblock else ''}"

        if self._embed_footer:
            self.embed.set_footer(text=self._embed_footer, icon_url=self.embed_footer_url or discord.embeds.EmptyEmbed)

    async def change_page(self, *, page: int) -> None:

        self.page = page
        await self.set_page(page=page)

        await self.message.edit(embed=self.embed)

    async def paginate(self) -> None:

        await super().paginate()

        await self.set_page(page=self.page)
        self.message = await self.ctx.reply(embed=self.embed, view=self.view)
