import json
from abc import ABC

from cogs.dashboard.utilities import objects, http
from cogs.dashboard.utilities.endpoint import BaseEndpoint


class Guilds(BaseEndpoint, ABC):

    async def get(self):

        user = await self.get_user()
        if not user:
            self.set_status(401)
            return await self.finish({'error': 'you need to like, log in and shit dude.'})

        data = json.loads(self.get_secure_cookie('access-token-response'))
        token = data.get('access_token')

        guilds_data = await self.bot.http_client.request(http.Route('GET', '/users/@me/guilds', token=token))
        guilds = [objects.Guild(guild_data) for guild_data in guilds_data]

        self.render('guilds.html', bot=self.bot, user=await self.get_user(), guilds=guilds,
                    invite_url=self.bot.invite_url)


def setup(**kwargs):
    return r'/guilds', Guilds, kwargs
