from abc import ABC

from cogs.dashboard.utilities.bases import BaseHTTPHandler

from cogs.voice.utilities.player import Player


# noinspection PyAsyncCall
class Dashboard(BaseHTTPHandler, ABC):

    async def get(self, guild_id):

        user = await self.get_user()
        if not user:
            self.set_status(401)
            return await self.finish({'error': 'you need to login to view this page.'})

        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return self.set_status(403)

        member = guild.get_member(int(user.id))
        if not member:
            return self.set_status(403)

        player = self.bot.diorite.get_player(guild, cls=Player)
        self.render('dashboard.html', bot=self.bot, user=user, guild=guild, player=player)


def setup(**kwargs):
    return [(r'/dashboard/(\d+)', Dashboard, kwargs)]
