"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see <https://www.gnu.org/licenses/>.
"""


import json
import time

from discord import Permissions


class TokenResponse:

    def __init__(self, data: dict):
        self.data = data

        self.refresh_token = self.data.get('refresh_token')
        self.access_token = self.data.get('access_token')
        self.token_type = self.data.get('token_type')
        self.expires_in = self.data.get('expires_in')
        self.scope = self.data.get('scope')

        self.fetch_time = self.data.get('fetch_time') or time.time()

    @property
    def has_expired(self):
        return (time.time() - self.fetch_time) > self.expires_in
    
    @property
    def json(self):
        data = self.data.copy()
        data['fetch_time'] = self.fetch_time
        return json.dumps(data)


class User:

    def __init__(self, data: dict):
        self.data = data

        self.id = data.get('id')
        self.username = data.get('username')
        self.discriminator = data.get('discriminator')
        self.avatar_hash = data.get('avatar')
        self.bot = data.get('bot')
        self.system = data.get('system')
        self.mfa_enabled = data.get('mfa_enabled')
        self.locale = data.get('locale')
        self.flags = data.get('flags')
        self.premium_type = data.get('premium_type')
        self.public_flags = data.get('public_flags')

        self.fetch_time = self.data.get('fetch_time') or time.time()

    @property
    def avatar(self):
        if not self.avatar_hash:
            return None
        avatar_format = '.gif' if self.avatar_hash.startswith('a_') else '.png'
        return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_hash}{avatar_format}?size=512'

    @property
    def name(self):
        return f'{self.username}#{self.discriminator}'

    @property
    def has_expired(self):
        return (time.time() - self.fetch_time) > 20

    @property
    def json(self):
        data = self.data.copy()
        data['fetch_time'] = self.fetch_time
        return json.dumps(data)


class Guild:

    def __init__(self, data: dict):
        self.data = data

        self.id = data.get('id')
        self.name = data.get('name')
        self.icon_hash = data.get('icon')
        self.owner = data.get('owner')
        self.permissions = Permissions(data.get('permissions'))
        self.features = data.get('features')

        self.fetch_time = self.data.get('fetch_time') or time.time()

    @property
    def icon(self):
        if not self.icon_hash:
            return None
        icon_format = '.gif' if self.icon_hash.startswith('a_') else '.png'
        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon_hash}{icon_format}?size=512'

    @property
    def has_expired(self):
        return (time.time() - self.fetch_time) > 10

    @property
    def json(self):
        data = self.data.copy()
        data['fetch_time'] = self.fetch_time
        return json.dumps(data)
