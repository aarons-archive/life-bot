from discord.ext import commands


class MusicEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_diorite_track_start(self, event):
        self.bot.dispatch('life_track_start', event.player.guild.id)

    @commands.Cog.listener()
    async def on_diorite_track_end(self, event):
        self.bot.dispatch('life_track_end', event.player.guild.id)

    @commands.Cog.listener()
    async def on_diorite_track_stuck(self, event):
        await event.player.channel.send('The current track got stuck while playing, ideally this should not happen so'
                                        'you can join my support server for more help.')
        self.bot.dispatch('life_track_end', event.player.guild.id)

    @commands.Cog.listener()
    async def on_diorite_track_error(self, event):
        await event.player.channel.send(f'Something went wrong while playing a track. Error: `{event.error}`')
        self.bot.dispatch('life_track_end', event.player.guild.id)

    @commands.Cog.listener()
    async def on_diorite_websocket_closed(self, event):
        await event.player.channel.send(f'This nodes websocket decided to disconnect, ideally this should not happen so'
                                        f'you can join my support server for more help.')


def setup(bot):
    bot.add_cog(MusicEvents(bot))
