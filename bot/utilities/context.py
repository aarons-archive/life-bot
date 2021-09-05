# Future
from __future__ import annotations

# Standard Library
import asyncio
import functools
from typing import TYPE_CHECKING, Any, Optional

# Packages
import discord
from discord.ext import commands

# My stuff
from core import colours, emojis
from utilities import exceptions, paginators, utils


if TYPE_CHECKING:
    # My stuff
    from core.bot import Life
    from extensions.voice.custom.player import Player


class Context(commands.Context):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.message: discord.Message = kwargs["message"]
        self.bot: Life = kwargs.get("bot")

    # Overwritten properties

    @property
    def voice_client(self) -> Optional[Player]:
        return self.guild.voice_client if self.guild else None

    @discord.utils.cached_property
    def author(self) -> discord.User | discord.Member:
        return self.message.author

    # Paginators

    async def paginate(
        self,
        *,
        entries: list[Any],
        per_page: int,
        timeout: int = 300,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> paginators.TextPaginator:

        paginator = paginators.TextPaginator(
            ctx=self,
            entries=entries,
            per_page=per_page,
            timeout=timeout,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
            header=header,
            footer=footer
        )

        await paginator.paginate()
        return paginator

    async def paginate_embed(
        self,
        *,
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
    ) -> paginators.EmbedPaginator:

        paginator = paginators.EmbedPaginator(
            ctx=self,
            entries=entries,
            per_page=per_page,
            timeout=timeout,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
            header=header,
            footer=footer,
            embed_footer=embed_footer,
            embed_footer_url=embed_footer_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            url=url,
            colour=colour,
        )

        await paginator.paginate()
        return paginator

    async def paginate_file(
        self,
        *,
        entries: list[functools.partial],
        timeout: int = 300,
        delete_message: bool = True,
        header: Optional[str] = None
    ) -> paginators.FilePaginator:

        paginator = paginators.FilePaginator(
            ctx=self,
            entries=entries,
            timeout=timeout,
            delete_message=delete_message,
            header=header
        )

        await paginator.paginate()
        return paginator

    async def paginate_embeds(
        self,
        *,
        entries: list[discord.Embed],
        timeout: int = 300,
        delete_message: bool = True,
    ) -> paginators.EmbedsPaginator:

        paginator = paginators.EmbedsPaginator(
            ctx=self,
            entries=entries,
            timeout=timeout,
            delete_message=delete_message,
        )

        await paginator.paginate()
        return paginator

    async def choice(
        self,
        *,
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
        colour: discord.Colour = colours.MAIN
    ) -> int:

        if len(entries) == 1:
            return 0

        paginator = paginators.EmbedPaginator(
            ctx=self,
            entries=entries,
            per_page=per_page,
            timeout=timeout,
            delete_message=delete_message,
            codeblock=codeblock,
            splitter=splitter,
            header=header,
            footer=footer,
            embed_footer_url=embed_footer_url,
            embed_footer=embed_footer,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            title=title,
            url=url,
            colour=colour
        )
        await paginator.paginate()

        for _ in range(5):

            try:
                response = await self.bot.wait_for("message", check=lambda msg: msg.author.id == self.author.id and msg.channel.id == self.channel.id, timeout=30.0)
            except asyncio.TimeoutError:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You took too long to respond, try again."
                )

            if response.content == "cancel":
                break

            try:
                number = int(response.content) - 1
            except (ValueError, KeyError):
                embed = utils.embed(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="That was not a valid choice, try again or send `cancel` to exit."
                )
                await self.reply(embed=embed)
                continue

            await paginator.stop()
            return number

        raise exceptions.EmbedError(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description="Exiting choice selection."
        )

    # Utilities

    async def try_dm(self, *args, **kwargs) -> Optional[discord.Message]:

        try:
            return await self.author.send(*args, **kwargs)
        except discord.Forbidden:
            try:
                return await self.reply(*args, **kwargs)
            except discord.Forbidden:
                return None
