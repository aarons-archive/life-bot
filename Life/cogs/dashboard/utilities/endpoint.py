import json
from abc import ABC

import tornado.web

from cogs.dashboard.utilities import http, objects


class BaseEndpoint(tornado.web.RequestHandler, ABC):

    def initialize(self, bot):
        self.bot = bot

    async def get_user(self):

        access_token_response = self.get_secure_cookie('access-token-response')

        if access_token_response:
            access_token_response = json.loads(access_token_response)
            access_token = access_token_response.get('access_token')
            user_data = await self.bot.http_client.request(http.Route('GET', '/users/@me', token=access_token))
            return objects.User(data=user_data)
        else:
            return None
