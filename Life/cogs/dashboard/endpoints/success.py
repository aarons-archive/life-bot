from abc import ABC
import json

from cogs.dashboard.utilities import endpoint


class Success(endpoint.BaseEndpoint, ABC):

    async def get(self):

        code = self.get_query_argument('code', None)
        if code is None:
            self.set_status(400)
            return await self.finish({'error': 'code not supplied'})

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = self.bot.config.auth_data.copy()
        data['code'] = code

        async with self.bot.session.post(self.bot.config.discord_auth_url, data=data, headers=headers) as response:
            access_token_response = await response.json()

        if access_token_response.get('error') is not None:
            self.set_status(400)
            return await self.finish({'error': 'invalid code supplied'})

        self.set_secure_cookie('access-token-response', json.dumps(access_token_response))
        return self.redirect(f'/guilds')


def setup(**kwargs):
    return r'/success', Success, kwargs
