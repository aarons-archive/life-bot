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

from __future__ import annotations

import asyncio
import functools
from typing import Any, Optional, TYPE_CHECKING, Union

import discord
from discord.ext import commands

from utilities import exceptions, objects, paginators


if TYPE_CHECKING:
    from cogs.voice.custom.player import Player
    from bot import Life


class Context(commands.Context):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.bot: Life = kwargs.get('bot')

    # Properties

    @property
    def voice_client(self) -> Optional[Player]:
        return self.guild.voice_client if self.guild else None

    # Custom properties

    @property
    def user_config(self) -> Union[objects.DefaultUserConfig, objects.UserConfig]:
        return self.bot.user_manager.get_config(getattr(self.author, 'id', None))

    @property
    def guild_config(self) -> Union[objects.DefaultGuildConfig, objects.GuildConfig]:
        return self.bot.guild_manager.get_config(getattr(self.guild, 'id', None))

    # Paginators

    async def paginate(
            self, *, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = '\n', header: Optional[str] = None,
            footer: Optional[str] = None
    ) -> paginators.TextPaginator:

        paginator = paginators.TextPaginator(
                ctx=self, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter, header=header, footer=footer
        )
        await paginator.paginate()

        return paginator

    async def paginate_embed(
            self, *, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = '\n', header: Optional[str] = None,
            footer: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None, colour: Optional[discord.Colour] = None, image: Optional[str] = None,
            thumbnail: Optional[str] = None, embed_footer: Optional[str] = None
    ) -> paginators.EmbedPaginator:

        paginator = paginators.EmbedPaginator(
                ctx=self, entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter, header=header,
                footer=footer, title=title, url=url, colour=colour, image=image, thumbnail=thumbnail, embed_footer=embed_footer
        )
        await paginator.paginate()

        return paginator

    async def paginate_file(
            self, *, entries: list[functools.partial], timeout: int = 300, delete_message: bool = True, header: Optional[str] = None, footer: Optional[str] = None
    ) -> paginators.FilePaginator:

        paginator = paginators.FilePaginator(ctx=self, entries=entries, timeout=timeout, delete_message=delete_message, header=header, footer=footer)
        await paginator.paginate()

        return paginator

    # Other paginators

    async def paginate_embeds(self, *, entries: list[discord.Embed], timeout: int = 300, delete_message: bool = True, content: Optional[str] = None) -> paginators.EmbedsPaginator:

        paginator = paginators.EmbedsPaginator(ctx=self, entries=entries, timeout=timeout, delete_message=delete_message, content=content)
        await paginator.paginate()

        return paginator

    async def choice(
            self, *, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = '\n', header: Optional[str] = None,
            footer: Optional[str] = None, title: Optional[str] = None, url: Optional[str] = None, colour: Optional[discord.Colour] = None, image: Optional[str] = None,
            thumbnail: Optional[str] = None, embed_footer: Optional[str] = None
    ) -> int:

        paginator = await self.paginate_embed(
                entries=entries, per_page=per_page, timeout=timeout, delete_message=delete_message, codeblock=codeblock, splitter=splitter, header=header, footer=footer,
                title=title, url=url, colour=colour, image=image, thumbnail=thumbnail, embed_footer=embed_footer
        )

        try:
            # noinspection PyTypeChecker
            response = await self.bot.wait_for('message', check=lambda msg: msg.author.id == self.author.id and msg.channel.id == self.channel.id, timeout=30.0)
        except asyncio.TimeoutError:
            raise exceptions.ArgumentError('You took too long to respond.')

        try:
            response = int(response.content) - 1
        except ValueError:
            raise exceptions.ArgumentError('That was not a valid number.')
        if response < 0 or response >= len(entries):
            raise exceptions.ArgumentError('That was not one of the available choices. Retry ')

        await paginator.stop()
        return response

    # Miscellaneous

    async def try_dm(self, **kwargs) -> Optional[discord.Message]:

        try:
            return await self.author.send(**kwargs)
        except discord.Forbidden:
            try:
                return await self.reply(**kwargs)
            except discord.Forbidden:
                return None
