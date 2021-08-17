from __future__ import annotations

import abc
from typing import Any, Optional

import discord

from core import config, emojis
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

    @discord.ui.button(emoji=emojis.FIRST)
    async def first(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == 0:
            return

        await self.paginator.change_page(page=0)

    @discord.ui.button(emoji=emojis.BACKWARD)
    async def backward(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page <= 0:
            return

        await self.paginator.change_page(page=self.paginator.page - 1)

    @discord.ui.button(label="1")
    async def page_label(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

    @discord.ui.button(emoji=emojis.FORWARD)
    async def forward(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page >= len(self.paginator.pages) - 1:
            return

        await self.paginator.change_page(page=self.paginator.page + 1)

    @discord.ui.button(emoji=emojis.LAST)
    async def last(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        if not self.paginator.message or self.paginator.page == len(self.paginator.pages) - 1:
            return

        await self.paginator.change_page(page=len(self.paginator.pages) - 1)

    @discord.ui.button(emoji=emojis.STOP)
    async def _stop(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        await self.paginator.stop(self.paginator.delete_message)
        self.stop()


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

    @discord.ui.button(emoji=emojis.STOP)
    async def _stop(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer()

        await self.paginator.stop(self.paginator.delete_message)
        self.stop()


class BasePaginator(abc.ABC):

    def __init__(
        self,
        *,
        ctx: context.Context,
        entries: list[Any],
        per_page: int,
        timeout: int = 300,
        delete_message: bool = True,
        codeblock: bool = False,
        splitter: str = "\n"
    ) -> None:

        self.ctx: context.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page

        self.timeout: int = timeout
        self.delete_message: bool = delete_message
        self.codeblock: bool = codeblock
        self.splitter: str = splitter

        self.message: Optional[discord.Message] = None
        self.view: Optional[PaginatorButtons | PaginatorStopButton] = None

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

        self.page = page
        await self.set_page(page=page)

        self.view.page_label.label = f"{page + 1}/{len(self.pages)}"

    @abc.abstractmethod
    async def paginate(self) -> None:
        self.view = PaginatorButtons(self) if len(self.pages) > 1 else PaginatorStopButton(self)
