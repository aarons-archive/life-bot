from discord.ext import commands
from cogs.utilities import exceptions
from cogs.voice.utilities import player
from cogs.utilities import paginators


class LifeContext(commands.Context):
    
    @property
    def player(self):
        
        if not self.bot.is_ready():
            raise exceptions.BotNotReadyError
        
        return self.bot.granitepy.get_player(self.guild, cls=player.Player)
    
    async def paginate(self, **kwargs):
        
        return await paginators.Paginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embed(self, **kwargs):
        
        return await paginators.EmbedPaginator(ctx=self, **kwargs).paginate()
    
    async def paginate_codeblock(self, **kwargs):
        
        return await paginators.CodeBlockPaginator(ctx=self, **kwargs).paginate()
    
    async def paginate_embeds(self, **kwargs):
        
        return await paginators.EmbedsPaginator(ctx=self, **kwargs).paginate()
