"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

from discord.ext import commands

from cogs.utilities import paginators
from cogs.voice.utilities.player import Player


class Context(commands.Context):

    @property
    def player(self):
        return self.bot.diorite.get_player(self.guild, cls=Player, text_channel=self.channel)

    async def paginate(self, **kwargs):
        await paginators.Paginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embed(self, **kwargs):
        await paginators.EmbedPaginator(ctx=self, **kwargs).paginate()
    
    async def paginate_codeblock(self, **kwargs):
        await paginators.CodeBlockPaginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embeds(self, **kwargs):
        await paginators.EmbedsPaginator(ctx=self, **kwargs).paginate()

    async def send_bin(self, content=None, **kwargs):

        if content:
            if len(content) > 2000:
                async with self.bot.session.post('https://mystb.in/documents', data=content.encode('utf-8')) as post:
                    post = await post.json()
                return await self.send(content=f'<https://mystb.in/{post["key"]}>', **kwargs)
            else:
                return await self.send(content=content, **kwargs)

        return await self.send(content=content, **kwargs)
