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

import asyncio
import functools
from typing import Any, Optional, TYPE_CHECKING, Union

import discord
from discord.ext import commands

from core import colours, emojis
from utilities import exceptions, objects, paginators


if TYPE_CHECKING:
    from extensions.voice.custom.player import Player
    from core.bot import Life


class Context(commands.Context):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.bot: Life = kwargs.get("bot")

    # Properties

    @property
    def voice_client(self) -> Optional[Player]:
        return self.guild.voice_client if self.guild else None

    # Custom properties

    @property
    def user_config(self) -> Union[objects.DefaultUserConfig, objects.UserConfig]:
        return self.bot.user_manager.get_config(getattr(self.author, "id", None))

    @property
    def guild_config(self) -> Union[objects.DefaultGuildConfig, objects.GuildConfig]:
        return self.bot.guild_manager.get_config(getattr(self.guild, "id", None))

    # Paginators

    async def paginate(
            self, *, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = "\n", header: Optional[str] = None,
            footer: Optional[str] = None
    ) -> paginators.TextPaginator:

        paginator = paginators.TextPaginator(
                ctx=self, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter, header=header, footer=footer
        )

        await paginator.paginate()
        return paginator

    async def paginate_embed(
            self, *, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = "\n", header: Optional[str] = None,
            footer: Optional[str] = None, embed_footer_url: Optional[str] = None, embed_footer: Optional[str] = None, image: Optional[str] = None, thumbnail: Optional[str] = None,
            author: Optional[str] = None, author_url: Optional[str] = None, author_icon_url: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None,
            colour: discord.Colour = colours.MAIN, additional_footer: Optional[str] = None
    ) -> paginators.EmbedPaginator:

        paginator = paginators.EmbedPaginator(
                ctx=self, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter, header=header, footer=footer,
                embed_footer_url=embed_footer_url, embed_footer=embed_footer, image=image, thumbnail=thumbnail, author=author, author_url=author_url, author_icon_url=author_icon_url, title=title,
                url=url, colour=colour, additional_footer=additional_footer
        )

        await paginator.paginate()
        return paginator

    async def paginate_file(
            self, *, entries: list[functools.partial], timeout: int = 300, delete_message: bool = True, header: Optional[str] = None
    ) -> paginators.FilePaginator:

        paginator = paginators.FilePaginator(
                ctx=self, entries=entries, timeout=timeout, delete_message=delete_message, header=header
        )

        await paginator.paginate()
        return paginator

    async def paginate_embeds(
            self, *, entries: list[discord.Embed], timeout: int = 300, delete_message: bool = True, content: Optional[str] = None
    ) -> paginators.EmbedsPaginator:

        paginator = paginators.EmbedsPaginator(
                ctx=self, entries=entries, timeout=timeout, delete_message=delete_message, content=content
        )

        await paginator.paginate()
        return paginator

    async def choice(
            self, *, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = "\n", header: Optional[str] = None,
            footer: Optional[str] = None, embed_footer_url: Optional[str] = None, embed_footer: Optional[str] = None, image: Optional[str] = None, thumbnail: Optional[str] = None,
            author: Optional[str] = None, author_url: Optional[str] = None, author_icon_url: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None,
            colour: discord.Colour = colours.MAIN
    ) -> int:

        if len(entries) == 1:
            return 0

        paginator = paginators.EmbedPaginator(
                ctx=self, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter, header=header, footer=footer,
                embed_footer_url=embed_footer_url, embed_footer=embed_footer, image=image, thumbnail=thumbnail, author=author, author_url=author_url, author_icon_url=author_icon_url, title=title,
                url=url, colour=colour
        )
        await paginator.paginate()

        for _ in range(5):

            try:
                # noinspection PyTypeChecker
                response = await self.bot.wait_for("message", check=lambda msg: msg.author.id == self.author.id and msg.channel.id == self.channel.id, timeout=30.0)
            except asyncio.TimeoutError:
                raise exceptions.EmbedError(colour=colours.RED, description=f"{emojis.CROSS}  You took too long to respond, try again.")

            if response.content == "cancel":
                break

            try:
                number = int(response.content) - 1
            except (ValueError, KeyError):
                embed = discord.Embed(colour=colours.RED, description=f"{emojis.CROSS}  That was not a valid choice, try again or send `cancel` to exit.")
                await self.reply(embed=embed)
                continue

            await paginator.stop(delete=True)
            return number

        raise exceptions.EmbedError(colour=colours.GREEN, description=f"{emojis.TICK}  Exiting choice selection.")

    # Miscellaneous

    async def try_dm(self, *args, **kwargs) -> Optional[discord.Message]:

        try:
            return await self.author.send(*args, **kwargs)
        except discord.Forbidden:
            try:
                return await self.reply(*args, **kwargs)
            except discord.Forbidden:
                return None
