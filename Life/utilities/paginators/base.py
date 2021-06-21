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

import abc
from typing import Any, Optional, TYPE_CHECKING

import discord
from discord import Interaction

import config
import emoji
from utilities import context, paginators


if TYPE_CHECKING:
    from bot import Life


class ButtonsView(discord.ui.View):

    def __init__(self, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

    async def interaction_check(self, interaction: Interaction) -> bool:
        return interaction.message.id == getattr(self.paginator.message, 'id', None) and interaction.user.id in {*config.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        await self.paginator.stop(delete=self.paginator.delete_message_when_done)

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        return

    @discord.ui.button(emoji=emoji.FIRST)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator.first()

    @discord.ui.button(emoji=emoji.BACKWARD)
    async def backward(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator.backward()

    @discord.ui.button(emoji=emoji.STOP)
    async def _stop(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator.stop()

    @discord.ui.button(emoji=emoji.FORWARD)
    async def forward(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator.forward()

    @discord.ui.button(emoji=emoji.LAST)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()
        await self.paginator.last()


class BasePaginator(abc.ABC):

    def __init__(
            self, *, ctx: context.Context, entries: list[Any], per_page: int, timeout: int = 300, delete_message_when_done: bool = False, codeblock: bool = False, splitter: str = '\n'
    ) -> None:

        self.bot: Life = ctx.bot
        self.ctx: context.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page

        self.timeout: int = timeout
        self.delete_message_when_done: bool = delete_message_when_done
        self.codeblock: bool = codeblock
        self.splitter: str = splitter

        self.message: Optional[discord.Message] = None
        self.view: Optional[discord.ui.View] = None

        self.page: int = 0

        self.pages = [self.splitter.join(self.entries[page:page + self.per_page]) for page in range(0, len(self.entries), self.per_page)] if self.per_page > 1 else self.entries

    # Abstract methods

    @abc.abstractmethod
    async def paginate(self) -> None:

        self.view = ButtonsView(self)

    @abc.abstractmethod
    async def first(self) -> None:

        if not self.message:
            return

        if self.page == 0:
            raise paginators.AlreadyOnPage

        self.page = 0

    @abc.abstractmethod
    async def backward(self) -> None:

        if not self.message:
            return

        if self.page <= 0:
            raise paginators.PageOutOfBounds

        self.page -= 1

    async def stop(self, delete: bool = False) -> None:

        await self.message.edit(view=None)

        if self.message and delete:
            await self.message.delete()
            self.message = None

    @abc.abstractmethod
    async def forward(self) -> None:

        if not self.message:
            return

        if self.page >= len(self.pages) - 1:
            raise paginators.PageOutOfBounds

        self.page += 1

    @abc.abstractmethod
    async def last(self) -> None:

        if not self.message:
            return

        if (page := len(self.pages) - 1) == self.page:
            raise paginators.AlreadyOnPage

        self.page = page
