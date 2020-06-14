from discord.ext import commands

from cogs.utilities import paginators, exceptions
from cogs.voice.utilities.player import Player


class Context(commands.Context):

    @property
    def player(self):

        if not self.bot.is_ready():
            raise exceptions.BotNotReadyError

        player = self.bot.diorite.get_player(self.guild, cls=Player)
        return player
    
    async def paginate(self, **kwargs):
        
        await paginators.Paginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embed(self, **kwargs):
        
        await paginators.EmbedPaginator(ctx=self, **kwargs).paginate()
    
    async def paginate_codeblock(self, **kwargs):
        
        await paginators.CodeBlockPaginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embeds(self, **kwargs):
        
        await paginators.EmbedsPaginator(ctx=self, **kwargs).paginate()
