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

import asyncio
from typing import Any, Optional, TYPE_CHECKING

import discord
from discord.ext import commands

import config
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
    def voice_client(self) -> Player:
        return self.guild.voice_client if self.guild else None

    # Custom properties

    @property
    def user_config(self) -> objects.UserConfig:
        return self.bot.user_manager.configs.get(getattr(self.author, 'id', None), self.bot.user_manager.default_config)

    @property
    def guild_config(self) -> objects.GuildConfig:
        return self.bot.guild_manager.configs.get(getattr(self.guild, 'id', None), self.bot.guild_manager.default_config)

    @property
    def colour(self) -> discord.Colour:

        if isinstance(self.author, discord.Member):  # skipcq: PTC-W0048
            if roles := list(reversed([role for role in self.author.roles if role.colour.value != 0])):
                return roles[0].colour

        return discord.Colour(config.COLOUR)

    # Main paginators

    async def paginate(self, **kwargs) -> paginators.TextPaginator:
        paginator = paginators.TextPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_embed(self, **kwargs) -> paginators.EmbedPaginator:
        paginator = paginators.EmbedPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_file(self, **kwargs) -> paginators.FilePaginator:
        paginator = paginators.FilePaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    # Other paginators

    async def paginate_embeds(self, **kwargs) -> paginators.EmbedsPaginator:
        paginator = paginators.EmbedsPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_choice(self, **kwargs) -> Any:

        paginator = await self.paginate_embed(**kwargs)

        try:
            response = await self.bot.wait_for('message', check=lambda msg: msg.author.id == self.author.id and msg.channel.id == self.channel.id, timeout=30.0)
        except asyncio.TimeoutError:
            raise exceptions.ArgumentError('You took too long to respond.')

        response = await commands.clean_content().convert(ctx=self, argument=response.content)
        try:
            response = int(response) - 1
        except ValueError:
            raise exceptions.ArgumentError('That was not a valid number.')
        if response < 0 or response >= len(kwargs.get('entries')):
            raise exceptions.ArgumentError('That was not one of the available choices.')

        await paginator.stop()
        return response

    # Other

    async def try_dm(self, **kwargs) -> Optional[discord.Message]:

        try:
            return await self.author.send(**kwargs)
        except discord.Forbidden:
            try:
                return await self.reply(**kwargs)
            except discord.Forbidden:
                return None
