from abc import ABC

from cogs.dashboard.utilities.endpoint import BaseEndpoint

from cogs.voice.utilities.player import Player


class Dashboard(BaseEndpoint, ABC):

    async def get(self, guild_id):

        user = await self.get_user()
        if not user:
            self.set_status(401)
            return await self.finish({'error': 'you need to like, log in and shit dude.'})

        guild = self.bot.get_guild(int(guild_id))
        player = self.bot.diorite.get_player(guild, cls=Player)

        self.render('dashboard.html', bot=self.bot, user=user, guild=guild, player=player)


def setup(**kwargs):
    return r'/dashboard/(\d+)', Dashboard, kwargs
