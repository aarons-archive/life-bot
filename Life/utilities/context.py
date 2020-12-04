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

import typing

from discord.ext import commands
import discord

from utilities import objects, paginators


class Context(commands.Context):

    @property
    def user_config(self) -> typing.Union[objects.DefaultUserConfig, objects.UserConfig]:

        if not self.author:
            return self.bot.user_manager.default_user_config

        return self.bot.user_manager.get_user_config(user_id=self.author.id)

    @property
    def guild_config(self) -> typing.Union[objects.DefaultGuildConfig, objects.GuildConfig]:

        if not self.guild:
            return self.bot.guild_manager.default_guild_config

        return self.bot.guild_manager.get_guild_config(guild_id=self.guild.id)

    @property
    def colour(self) -> discord.Colour:

        if isinstance(self.user_config, objects.DefaultUserConfig):
            return self.guild_config.colour

        return self.user_config.colour

    async def paginate(self, **kwargs) -> paginators.Paginator:
        paginator = paginators.Paginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_embed(self, **kwargs) -> paginators.EmbedPaginator:
        paginator = paginators.EmbedPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator

    async def paginate_embeds(self, **kwargs) -> paginators.EmbedsPaginator:
        paginator = paginators.EmbedsPaginator(ctx=self, **kwargs)
        await paginator.paginate()
        return paginator
