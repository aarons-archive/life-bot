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

import colours
import config
from utilities import context, paginators


class EmbedPaginator(paginators.BasePaginator):

    def __init__(
            self, *, ctx: context.Context, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = '\n',
            header: Optional[str] = None, footer: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None, colour: Optional[discord.Colour] = None, image: Optional[str] = None,
            thumbnail: Optional[str] = None, embed_footer: Optional[str] = None
    ) -> None:
        super().__init__(ctx=ctx, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter)

        self.header: str = header or ''
        self.footer: str = footer or ''

        self.embed_title: Optional[str] = title
        self.embed_url: Optional[str] = url
        self.embed_colour: discord.Colour = colour or colours.MAIN
        self.embed_image: Optional[str] = image
        self.embed_thumbnail: Optional[str] = thumbnail
        self._embed_footer: Optional[str] = embed_footer

        self.embed: discord.Embed = discord.Embed(colour=self.embed_colour, title=self.embed_title or discord.embeds.EmptyEmbed, url=self.embed_url or discord.embeds.EmptyEmbed)

        if self.embed_image:
            self.embed.set_image(url=self.embed_image)
        if self.embed_thumbnail:
            self.embed.set_thumbnail(url=self.embed_thumbnail)

    # Properties

    @property
    def embed_footer(self) -> str:
        return (self._embed_footer or f'\n\nPage: {self.page + 1}/{len(self.pages)} | Total entries: {len(self.entries)}') if len(self.pages) != 1 else discord.embeds.EmptyEmbed

    # Page generator

    def generate_page(self, page: int = 0) -> str:
        return f'{f"```{config.NL}" if self.codeblock else ""}{self.header}{self.pages[page]}{self.footer}{f"{config.NL}```" if self.codeblock else ""}'

    # Abstract methods

    async def paginate(self) -> None:

        await super().paginate()

        self.embed.description = self.generate_page(self.page)
        self.embed.set_footer(text=self.embed_footer)

        self.message = await self.ctx.reply(embed=self.embed, view=self.view)

    async def first(self) -> None:

        await super().first()

        self.embed.description = self.generate_page(self.page)
        self.embed.set_footer(text=self.embed_footer)

        await self.message.edit(embed=self.embed)

    async def backward(self) -> None:

        await super().backward()

        self.embed.description = self.generate_page(self.page)
        self.embed.set_footer(text=self.embed_footer)

        await self.message.edit(embed=self.embed)

    async def forward(self) -> None:

        await super().forward()

        self.embed.description = self.generate_page(self.page)
        self.embed.set_footer(text=self.embed_footer)

        await self.message.edit(embed=self.embed)

    async def last(self) -> None:

        await super().last()

        self.embed.description = self.generate_page(self.page)
        self.embed.set_footer(text=self.embed_footer)

        await self.message.edit(embed=self.embed)
