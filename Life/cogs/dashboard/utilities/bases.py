"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""


import binascii
import json
import os
from abc import ABC

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from cogs.dashboard.utilities import http, objects


# noinspection PyAttributeOutsideInit
class BaseHTTPHandler(RequestHandler, ABC):

    def initialize(self, bot):
        self.bot = bot

    async def prepare(self):

        identifier = self.get_secure_cookie('identifier')
        if identifier is None:
            self.set_secure_cookie('identifier', binascii.hexlify(os.urandom(16)).decode('utf-8'))

    async def get_token(self):

        identifier = self.get_secure_cookie('identifier')

        token_response = await self.bot.redis.hget('tokens', identifier)
        if not token_response:
            return None

        token_response = objects.TokenResponse(data=json.loads(token_response.decode()))
        if token_response.has_expired:

            url = f'https://discord.com/api/oauth2/token'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'client_secret': self.bot.config.client_secret,
                'redirect_uri': self.bot.config.redirect_uri,
                'client_id': self.bot.config.client_id,
                'grant_type': 'refresh_token',
                'scope': 'identify guilds',
                'refresh_token': token_response.refresh_token
            }

            async with self.bot.session.post(url, data=data, headers=headers) as response:
                data = await response.json()

            error = data.get('error')
            if error is not None:
                self.set_status(400)
                return await self.finish({'error': error})

            token_response = objects.TokenResponse(data=data)
            await self.bot.redis.hset('tokens', identifier, token_response.json)

        return token_response

    async def fetch_user(self):

        identifier = self.get_secure_cookie('identifier')

        token_response = await self.get_token()
        if not token_response:
            return None

        route = http.Route('GET', '/users/@me', token=token_response.access_token)
        user_data = await self.bot.http_client.request(route)
        user = objects.User(data=user_data)

        await self.bot.redis.set(identifier, user.json)
        return user

    async def get_user(self):

        identifier = self.get_secure_cookie('identifier')

        user_data = await self.bot.redis.get(identifier)
        if not user_data:
            return await self.fetch_user()

        user = objects.User(data=json.loads(user_data.decode()))
        if user.has_expired:
            return await self.fetch_user()

        return user

    async def fetch_guilds(self):

        token_response = await self.get_token()
        if not token_response:
            return None

        route = http.Route('GET', '/users/@me/guilds', token=token_response.access_token)
        guild_data = await self.bot.http_client.request(route)
        guilds = [objects.Guild(guild_data) for guild_data in guild_data]

        return guilds


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class BaseWebsocketHandler(WebSocketHandler, ABC):

    def initialize(self, bot):
        self.bot = bot
        self.authenticated = False
