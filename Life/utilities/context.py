"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import typing

from discord.ext import commands
import discord

from cogs.voice.utilities.player import Player
from utilities import objects, paginators


class Context(commands.Context):

    @property
    def user_config(self) -> typing.Union[objects.DefaultUserConfig, objects.UserConfig]:

        if not self.author:
            return self.bot.default_user_config

        return self.bot.get_user_config(user=self.author)

    @property
    def guild_config(self) -> typing.Union[objects.DefaultGuildConfig, objects.GuildConfig]:

        if not self.guild:
            return self.bot.default_guild_config

        return self.bot.get_guild_config(guild=self.guild)

    @property
    def colour(self) -> discord.Colour:

        if isinstance(self.user_config, objects.DefaultUserConfig):
            return self.guild_config.colour

        return self.user_config.colour

    @property
    def player(self) -> Player:
        return self.bot.diorite.get_player(self.guild, cls=Player, text_channel=self.channel)

    async def paginate(self, **kwargs) -> None:
        await paginators.Paginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embed(self, **kwargs) -> None:
        await paginators.EmbedPaginator(ctx=self, **kwargs).paginate()

    async def paginate_embeds(self, **kwargs) -> None:
        await paginators.EmbedsPaginator(ctx=self, **kwargs).paginate()
