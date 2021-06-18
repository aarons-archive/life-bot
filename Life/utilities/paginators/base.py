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

import abc
import asyncio
import contextlib
from typing import Any, Optional, TYPE_CHECKING

import async_timeout
import discord

import config
import emoji
from utilities import context, paginators


if TYPE_CHECKING:
    from bot import Life


class BasePaginator(abc.ABC):

    __slots__ = 'bot', 'ctx', 'entries', 'per_page', 'timeout', 'delete_message_when_done', 'delete_reactions_when_done', 'codeblock', 'splitter', 'reaction_event', 'task', 'message', 'looping', \
                'page', 'BUTTONS', 'pages'

    def __init__(
            self, *, bot: Life = None, ctx: context.Context, entries: list[Any], per_page: int, timeout: int = 300, delete_message_when_done: bool = False, delete_reactions_when_done: bool = True,
            codeblock: bool = False, splitter: str = '\n'
    ) -> None:

        self.bot: Life = bot or ctx.bot
        self.ctx: context.Context = ctx
        self.entries: list[Any] = entries
        self.per_page: int = per_page

        self.timeout: int = timeout
        self.delete_message_when_done: bool = delete_message_when_done
        self.delete_reactions_when_done: bool = delete_reactions_when_done
        self.codeblock: bool = codeblock
        self.splitter: str = splitter

        self.reaction_event: asyncio.Event = asyncio.Event()

        self.task: Optional[asyncio.Task] = None
        self.message: Optional[discord.Message] = None

        self.looping: bool = True
        self.page: int = 0

        self.BUTTONS = {
            emoji.PREVIOUS:    self.first,
            emoji.ARROW_LEFT:  self.backward,
            emoji.STOP:        self.stop,
            emoji.ARROW_RIGHT: self.forward,
            emoji.NEXT:        self.last
        }

        self.pages = [self.splitter.join(self.entries[page:page + self.per_page]) for page in range(0, len(self.entries), self.per_page)] if self.per_page > 1 else self.entries

    # Checks

    def check_reaction(self, payload: discord.RawReactionActionEvent) -> bool:

        if str(payload.emoji) not in self.BUTTONS.keys():
            return False

        if payload.message_id != getattr(self.message, 'id', None) or payload.channel_id != getattr(getattr(self.message, 'channel', None), 'id', None):
            return False

        return payload.user_id in {*config.OWNER_IDS, self.ctx.author.id}

    # Listeners

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        await self.handle_reaction(payload)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        await self.handle_reaction(payload)

    async def handle_reaction(self, payload: discord.RawReactionActionEvent) -> None:

        if not self.check_reaction(payload) or not self.looping:
            return

        self.reaction_event.set()
        with contextlib.suppress(paginators.AlreadyOnPage, paginators.PageOutOfBounds):
            await self.BUTTONS[str(payload.emoji)]()

    # Loop

    async def loop(self) -> None:

        if len(self.pages) == 1:
            await self.message.add_reaction(':stop:737826951980646491')
        else:
            for emote in self.BUTTONS:
                await self.message.add_reaction(emote)

        #

        while self.looping:
            try:
                async with async_timeout.timeout(self.timeout):
                    await self.reaction_event.wait()
                    self.reaction_event.clear()
            except asyncio.TimeoutError:
                self.looping = False
            else:
                continue

        #

        if self.message and self.delete_reactions_when_done:
            for reaction in self.BUTTONS:
                await self.message.remove_reaction(reaction, self.bot.user)
            await self.stop(delete=False)
        else:
            await self.stop(delete=self.delete_message_when_done)

    # Abstract methods

    @abc.abstractmethod
    async def paginate(self) -> None:

        self.task = asyncio.create_task(self.loop())

        self.bot.add_listener(self.on_raw_reaction_add)
        self.bot.add_listener(self.on_raw_reaction_remove)

    @abc.abstractmethod
    async def first(self) -> None:

        if self.page == 0:
            raise paginators.AlreadyOnPage

        self.page = 0

    @abc.abstractmethod
    async def backward(self) -> None:

        if self.page <= 0:
            raise paginators.PageOutOfBounds

        self.page -= 1

    async def stop(self, delete: bool = True) -> None:

        self.task.cancel()
        self.looping = False

        if self.message and delete:
            await self.message.delete()
            self.message = None

        self.bot.remove_listener(self.on_raw_reaction_add)
        self.bot.remove_listener(self.on_raw_reaction_remove)

    @abc.abstractmethod
    async def forward(self) -> None:

        if self.page >= len(self.pages) - 1:
            raise paginators.PageOutOfBounds

        self.page += 1

    @abc.abstractmethod
    async def last(self) -> None:

        if (page := len(self.pages) - 1) == self.page:
            raise paginators.AlreadyOnPage

        self.page = page
