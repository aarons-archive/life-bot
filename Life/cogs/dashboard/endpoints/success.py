from abc import ABC

from cogs.dashboard.utilities import endpoint


class Success(endpoint.BaseEndpoint, ABC):

    async def get(self):

        code = self.get_query_argument('code', None)
        if code is None:
            self.set_status(400)
            return await self.finish({'error': 'code not supplied'})

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = self.bot.config.DISCORD_AUTH_DATA.copy()
        data['code'] = code

        async with self.bot.session.post(self.bot.config.DISCORD_AUTH_URL, data=data, headers=headers) as response:
            access_token_response = await response.text()

        self.set_secure_cookie('access-token-response', access_token_response)
        return self.redirect(f'/guilds')


def setup(**kwargs):
    return r'/success', Success, kwargs
