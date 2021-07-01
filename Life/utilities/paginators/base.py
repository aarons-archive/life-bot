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
from typing import Any, Optional

import discord

import config
import emojis
from utilities import context


class PaginatorButtons(discord.ui.View):

    def __init__(self, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

    #

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.message.id == getattr(self.paginator.message, "id", None) and interaction.user.id in {*config.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        await self.paginator.stop(delete=self.paginator.delete_message)

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        return

    #

    # noinspection PyUnusedLocal
    @discord.ui.button(emoji=emojis.FIRST)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == 0:
            return

        await self.paginator.change_page(page=0)

    # noinspection PyUnusedLocal
    @discord.ui.button(emoji=emojis.BACKWARD)
    async def backward(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page <= 0:
            return

        await self.paginator.change_page(page=self.paginator.page - 1)

    # noinspection PyUnusedLocal
    @discord.ui.button(emoji=emojis.STOP)
    async def _stop(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        await self.paginator.stop(self.paginator.delete_message)
        self.stop()

    # noinspection PyUnusedLocal
    @discord.ui.button(emoji=emojis.FORWARD)
    async def forward(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page >= len(self.paginator.pages) - 1:
            return

        await self.paginator.change_page(page=self.paginator.page + 1)

    # noinspection PyUnusedLocal
    @discord.ui.button(emoji=emojis.LAST)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == len(self.paginator.pages) - 1:
            return

        await self.paginator.change_page(page=len(self.paginator.pages) - 1)


class PaginatorStopButton(discord.ui.View):

    def __init__(self, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

    #

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.message.id == getattr(self.paginator.message, "id", None) and interaction.user.id in {*config.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        await self.paginator.stop(delete=self.paginator.delete_message)

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        return

    #

    # noinspection PyUnusedLocal
    @discord.ui.button(emoji=emojis.STOP)
    async def _stop(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        await self.paginator.stop(self.paginator.delete_message)
        self.stop()


class BasePaginator(abc.ABC):

    def __init__(
            self, *, ctx: context.Context, entries: list[Any], per_page: int, timeout: int = 300, delete_message: bool = True, codeblock: bool = False, splitter: str = "\n"
    ) -> None:

        self.ctx: context.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page

        self.timeout: int = timeout
        self.delete_message: bool = delete_message
        self.codeblock: bool = codeblock
        self.splitter: str = splitter

        self.message: Optional[discord.Message] = None
        self.view: Optional[discord.ui.View] = None

        self.page: int = 0
        self.current_page: Optional[Any] = None

        self.pages = [self.splitter.join(self.entries[page:page + self.per_page]) for page in range(0, len(self.entries), self.per_page)] if self.per_page > 1 else self.entries

    #

    async def stop(self, delete: bool) -> None:

        if self.message:
            if delete:
                await self.message.delete()
                self.message = None
            else:
                await self.message.edit(view=None)
                self.view = None

    # Abstract methods

    @abc.abstractmethod
    async def set_page(self, *, page: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def change_page(self, *, page: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def paginate(self) -> None:
        self.view = PaginatorButtons(self) if len(self.pages) > 1 else PaginatorStopButton(self)
