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

import json
import time
import typing

import discord


class TokenResponse:

    def __init__(self, data: dict) -> None:
        self.data = data

        self.access_token: str  = data.get('access_token')
        self.token_type: str    = data.get('token_type')
        self.expires_in: int    = data.get('expires_in')
        self.refresh_token: str = data.get('refresh_token')
        self.scope: str         = data.get('scope')

    @property
    def fetch_time(self) -> float:

        fetch_time = self.data.get('fetch_time')
        if fetch_time:
            return fetch_time

        return time.time()

    @property
    def has_expired(self) -> bool:
        return (time.time() - self.fetch_time) > self.expires_in
    
    @property
    def json(self) -> str:

        data = self.data.copy()
        data['fetch_time'] = self.fetch_time
        return json.dumps(data)


class User:

    def __init__(self, data: dict) -> None:
        self.data = data

        self.id: int                           = data.get('id')
        self.username: str                     = data.get('username')
        self.discriminator: str                = data.get('discriminator')
        self.avatar_hash: typing.Optional[str] = data.get('avatar')
        self.bot: bool                         = data.get('bot')
        self.system: bool                      = data.get('system')
        self.mfa_enabled: bool                 = data.get('mfa_enabled')
        self.locale: str                       = data.get('locale')
        self.flags: int                        = data.get('flags')
        self.premium_type: int                 = data.get('premium_type')
        self.public_flags: int                 = data.get('public_flags')

    @property
    def avatar(self) -> typing.Optional[str]:

        if not self.avatar_hash:
            return None

        return f'https://cdn.discordapp.com/avatars/{self.id}/{self.avatar_hash}{".gif" if self.avatar_hash.startswith("a_") else ".png"}?size=512'

    @property
    def name(self) -> str:
        return f'{self.username}#{self.discriminator}'

    @property
    def fetch_time(self) -> float:

        fetch_time = self.data.get('fetch_time')
        if fetch_time:
            return fetch_time

        return time.time()

    @property
    def has_expired(self) -> bool:
        return (time.time() - self.fetch_time) > 20

    @property
    def json(self) -> str:

        data = self.data.copy()
        data['fetch_time'] = self.fetch_time
        return json.dumps(data)


class Guild:

    def __init__(self, data: dict) -> None:
        self.data = data

        self.id: int                          = data.get('id')
        self.name: str                        = data.get('name')
        self.icon_hash: typing.Optional[str]  = data.get('icon')
        self.owner: bool                      = data.get('owner')
        self.permissions: discord.Permissions = discord.Permissions(int(data.get('permissions_new')))
        self.features: typing.List[str]       = data.get('features')

    @property
    def icon(self) -> typing.Optional[str]:

        if not self.icon_hash:
            return None

        return f'https://cdn.discordapp.com/icons/{self.id}/{self.icon_hash}{".gif" if self.icon_hash.startswith("a_") else ".png"}?size=512'

    @property
    def fetch_time(self) -> float:

        fetch_time = self.data.get('fetch_time')
        if fetch_time:
            return fetch_time

        return time.time()

    @property
    def has_expired(self) -> bool:
        return (time.time() - self.fetch_time) > 20

    @property
    def json(self) -> str:

        data = self.data.copy()
        data['fetch_time'] = self.fetch_time
        return json.dumps(data)
