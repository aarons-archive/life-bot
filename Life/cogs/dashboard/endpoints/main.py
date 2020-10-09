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

import pendulum

from cogs.dashboard.utilities import objects
from cogs.dashboard.utilities.bases import BaseHTTPHandler
from utilities import exceptions


# noinspection PyAsyncCall
class Index(BaseHTTPHandler, ABC):

    async def get(self):
        self.render('index.html', bot=self.bot, user=await self.get_user())


# noinspection PyAsyncCall
class Login(BaseHTTPHandler, ABC):

    async def get(self):

        identifier = self.get_secure_cookie('identifier')
        user_state = self.get_secure_cookie('state')
        auth_state = self.get_query_argument('state', None)
        code = self.get_query_argument('code', None)

        if not code or not auth_state or not user_state:

            state = binascii.hexlify(os.urandom(16)).decode()
            self.set_secure_cookie('state', state)

            url = f'https://discord.com/api/oauth2/authorize?client_id={self.bot.config.client_id}&response_type=code' \
                  f'&scope=identify%20guilds&redirect_uri={self.bot.config.login_redirect_uri}&state={state}'
            return self.redirect(url)

        if not auth_state == user_state.decode():
            self.set_status(400)
            return await self.finish({'error': 'user state and server state must match.'})

        self.clear_cookie('state')

        url = f'https://discord.com/api/oauth2/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_secret': self.bot.config.client_secret,
            'client_id': self.bot.config.client_id,
            'redirect_uri': self.bot.config.redirect_uri,
            'code': code,
            'grant_type': 'authorization_code',
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

        return self.redirect(f'/profile')


# noinspection PyAsyncCall
class Profile(BaseHTTPHandler, ABC):

    async def get(self):

        user = await self.get_user()
        if not user:
            self.set_status(401)
            return await self.finish({'error': 'you need to login to view this page.'})

        self.render('profile.html', bot=self.bot, user=user, guilds=await self.fetch_guilds())


# noinspection PyAsyncCall
class Timezones(BaseHTTPHandler, ABC):

    async def get(self):
        self.render('timezones.html', bot=self.bot, timezones=pendulum.timezones, user=await self.get_user())


def setup(**kwargs):
    return [('/', Index, kwargs), ('/login', Login, kwargs), ('/profile', Profile, kwargs), ('/timezones', Timezones, kwargs)]
