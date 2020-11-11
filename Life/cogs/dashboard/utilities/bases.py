#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

import binascii
import json
import os
import typing
from abc import ABC

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from bot import Life
from cogs.dashboard.utilities import http, objects
from utilities import exceptions


# noinspection PyAttributeOutsideInit
class BaseHTTPHandler(RequestHandler, ABC):

    def initialize(self, bot: Life) -> None:
        self.bot = bot

    async def prepare(self) -> None:

        identifier = self.get_secure_cookie('identifier')
        if identifier is None:
            self.set_secure_cookie('identifier', binascii.hexlify(os.urandom(16)).decode('utf-8'))

    async def get_token(self) -> typing.Optional[objects.TokenResponse]:

        identifier = self.get_secure_cookie('identifier')

        token_response_data = await self.bot.redis.hget('tokens', identifier)
        if not token_response_data:
            return None

        token_response = objects.TokenResponse(data=json.loads(token_response_data.decode()))
        if token_response.has_expired:

            url = 'https://discord.com/api/oauth2/token'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'client_secret': self.bot.config.client_secret,
                'client_id': self.bot.config.client_id,
                'redirect_uri': self.bot.config.redirect_uri,
                'refresh_token': token_response.refresh_token,
                'grant_type': 'refresh_token',
                'scope': 'identify guilds',
            }

            async with self.bot.session.post(url, data=data, headers=headers) as response:
                if 200 < response.status > 206:
                    raise exceptions.HTTPError(json.dumps(await response.json()))

                data = await response.json()

            if data.get('error'):
                raise exceptions.HTTPError(json.dumps(data))

            token_response = objects.TokenResponse(data=data)
            await self.bot.redis.hset('tokens', identifier, token_response.json)

        return token_response

    async def fetch_user(self) -> typing.Optional[objects.User]:

        identifier = self.get_secure_cookie('identifier')

        token_response = await self.get_token()
        if not token_response:
            return None

        user_data = await self.bot.http_client.request(http.Route('GET', '/users/@me', token=token_response.access_token))

        user = objects.User(data=user_data)
        await self.bot.redis.set(identifier, user.json)

        return user

    async def get_user(self) -> typing.Optional[objects.User]:

        identifier = self.get_secure_cookie('identifier')

        user_data = await self.bot.redis.get(identifier)
        if not user_data:
            user = await self.fetch_user()
        else:
            user = objects.User(data=json.loads(user_data.decode()))
            if user.has_expired:
                user = await self.fetch_user()

        return user

    async def fetch_guilds(self) -> typing.Optional[typing.List[objects.Guild]]:

        token_response = await self.get_token()
        if not token_response:
            return

        user = await self.get_user()
        if not user:
            return

        guild_data = await self.bot.http_client.request(http.Route('GET', '/users/@me/guilds', token=token_response.access_token))

        guilds = [objects.Guild(guild_data) for guild_data in guild_data]
        await self.bot.redis.hset('guilds', user.id, json.dumps([guild.json for guild in guilds]))

        return guilds

    async def get_guilds(self) -> typing.Optional[typing.List[objects.Guild]]:

        token_response = await self.get_token()
        if not token_response:
            return

        user = await self.get_user()
        if not user:
            return

        guilds_data = await self.bot.redis.hget('guilds', user.id)
        if not guilds_data:
            guilds = await self.fetch_guilds()
        else:
            guilds = [objects.Guild(guild_data) for guild_data in json.loads(guilds_data.decode())]
            if any(guild.has_expired for guild in guilds):
                guilds = await self.fetch_guilds()

        return guilds


# noinspection PyAttributeOutsideInit
class BaseWebsocketHandler(WebSocketHandler, ABC):

    def initialize(self, bot: Life) -> None:
        self.bot = bot
        self.authenticated = False
