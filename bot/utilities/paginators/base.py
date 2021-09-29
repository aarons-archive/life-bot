# Future
from __future__ import annotations

# Standard Library
import abc
from typing import Any

# Packages
import discord

# My stuff
from core import config, emojis, values
from core.bot import Life
from utilities import context


class PaginatorButtons(discord.ui.View):

    def __init__(self, *, paginator: BasePaginator) -> None:
        super().__init__(timeout=paginator.timeout)

        self.paginator: BasePaginator = paginator

    # Overridden

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in {*config.OWNER_IDS, self.paginator.ctx.author.id}

    async def on_timeout(self) -> None:
        self.stop()
        await self.paginator.stop()

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        return

    # Buttons

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

    @discord.ui.button(label="1/?")
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

        self.stop()
        await self.paginator.stop()


class BasePaginator(abc.ABC):

    def __init__(
        self,
        *,
        ctx: context.Context[Life],
        entries: list[Any],
        per_page: int,
        timeout: int = 300,
        delete_message: bool = False,
        codeblock: bool = False,
        splitter: str = "\n",
    ) -> None:

        self.ctx: context.Context[Life] = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page

        self.timeout: int = timeout
        self.delete_message: bool = delete_message
        self.codeblock: bool = codeblock
        self.splitter: str = splitter

        self.message: discord.Message | None = None
        self.view: PaginatorButtons = PaginatorButtons(paginator=self)

        self.page: int = 0

        if self.per_page > 1:
            self.pages: list[Any] = [self.splitter.join(self.entries[page:page + self.per_page]) for page in range(0, len(self.entries), self.per_page)]
        else:
            self.pages: list[Any] = self.entries

        self.CODEBLOCK_START = f"```{values.NL}" if self.codeblock else ""
        self.CODEBLOCK_END = f"{values.NL}```" if self.codeblock else ""

    #

    async def stop(self) -> None:

        if not self.message:
            return

        if self.delete_message:
            await self.message.delete()
        else:
            await self.message.edit(content="*Message was deleted.*", embed=None, view=None)

        self.message = None

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
        raise NotImplementedError
