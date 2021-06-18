#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

import discord

import config
from utilities import context, paginators


if TYPE_CHECKING:
    from bot import Life


class EmbedPaginator(paginators.BasePaginator):

    __slots__ = 'bot', 'ctx', 'entries', 'per_page', 'timeout', 'delete_messages_when_done', 'delete_reactions_when_done', 'codeblock', 'splitter', 'reaction_event', 'task', 'message', 'looping', \
                'page', 'BUTTONS', 'header', 'footer', 'embed_title', 'embed_url', 'embed_colour', 'embed_image', 'embed_thumbnail', '_embed_footer', 'embed'

    def __init__(
            self, *, bot: Life = None, ctx: context.Context, entries: list[Any], per_page: int, timeout: int = 300, delete_message_when_done: bool = False, delete_reactions_when_done: bool = True,
            codeblock: bool = False, splitter: str = '\n', header: Optional[str] = None, footer: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None,
            colour: Optional[discord.Colour] = None, image: Optional[str] = None, thumbnail: Optional[str] = None, embed_footer: Optional[str] = None
    ) -> None:
        super().__init__(
                bot=bot, ctx=ctx, entries=entries, per_page=per_page, timeout=timeout, delete_message_when_done=delete_message_when_done, delete_reactions_when_done=delete_reactions_when_done,
                codeblock=codeblock, splitter=splitter
        )

        self.header: str = header or ''
        self.footer: str = footer or ''

        self.embed_title: Optional[str] = title
        self.embed_url: Optional[str] = url
        self.embed_colour = discord.Colour = colour or config.MAIN
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
        return self._embed_footer or f'\n\nPage: {self.page + 1}/{len(self.pages)} | Total entries: {len(self.entries)}'

    # Page generator

    def generate_page(self, page: int = 0) -> str:
        return f'{f"```{config.NL}" if self.codeblock else ""}{self.header}{self.pages[page]}{self.footer}{f"{config.NL}```" if self.codeblock else ""}'

    # Abstract methods

    async def paginate(self) -> None:

        self.embed.description = self.generate_page(self.page)
        self.embed.set_footer(text=self.embed_footer)

        self.message = await self.ctx.reply(embed=self.embed)
        await super().paginate()

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
