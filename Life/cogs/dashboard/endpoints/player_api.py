import asyncio
import json
from abc import ABC
from typing import Union

from cogs.dashboard.utilities.bases import BaseWebsocketHandler
from cogs.dashboard.utilities import objects
from cogs.voice.utilities.player import Player
from tornado.web import decode_signed_value


class Websocket(BaseWebsocketHandler, ABC):

    async def open(self):
        self.authenticated = False
        return await self.write_message({'op': 1, 'data': 'waiting for identify'})

    async def on_message(self, message: Union[str, bytes]):

        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            return self.close(code=4001, reason='invalid payload received')

        op = message.get('op')

        if op == 0:  # DISPATCH
            return self.close(code=4002, reason='invalid op code, code 0 must only be sent by server.')

        elif op == 1:  # HELLO
            return self.close(code=4002, reason='invalid op code, code 1 must only be sent by server.')

        elif op == 2:  # IDENTIFY

            if self.authenticated is True:
                return self.close(code=4004, reason='already authenticated')

            data = message.get('data')

            guild = self.bot.get_guild(int(data.get('guild_id')))
            if not guild:
                return self.close(code=4006, reason='invalid guild id provided')

            identifier = decode_signed_value(secret=self.application.settings["cookie_secret"], name='identifier',
                                             value=data.get('identifier').strip('"'))

            if identifier is None:
                identifier = data.get('identifier').strip('"')

            token_response = await self.bot.redis.hget('tokens', identifier)
            if not token_response:
                return self.close(code=4003, reason='not logged in with discord')

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
                    return self.close(code=4000, reason=error)

                token_response = objects.TokenResponse(data=data)
                await self.bot.redis.hset('tokens', data.get('token'), token_response.json)

            self.authenticated = True
            self.guild = guild
            self.player = self.bot.diorite.get_player(guild, cls=Player)

            self.send_current_task = asyncio.create_task(self.send_current())
            self.send_player_task = asyncio.create_task(self.send_player())
            self.send_position_task = asyncio.create_task(self.send_position())

        elif self.authenticated is False:
            return self.close(code=4005, reason='not authenticated')

    async def send_current(self):

        current_data = getattr(self.player.current, 'json', None)
        await self.write_message({'op': 0, 'event': 'CURRENT', 'data': current_data})

        self.last_current_data = current_data

        while True:

            current_data = getattr(self.player.current, 'json', None)

            if current_data == self.last_current_data:
                await asyncio.sleep(1)
                continue

            self.last_current_data = current_data

            await self.write_message({'op': 0, 'event': 'CURRENT', 'data': current_data})
            await asyncio.sleep(1)

    async def send_player(self):

        player_data = {
            'voice_channel_id': str(getattr(self.player.voice_channel, 'id', None)),
            'text_channel_id': str(getattr(self.player.text_channel, 'id', None)),
            'looping': self.player.looping,
            'volume': self.player.volume,
            'paused': self.player.paused,
        }
        await self.write_message({'op': 0, 'event': 'PLAYER', 'data': player_data})

        self.last_player_data = player_data

        while True:

            player_data = {
                'voice_channel_id': str(getattr(self.player.voice_channel, 'id', None)),
                'text_channel_id': str(getattr(self.player.text_channel, 'id', None)),
                'looping': self.player.looping,
                'volume': self.player.volume,
                'paused': self.player.paused,
            }

            if player_data == self.last_player_data:
                await asyncio.sleep(1)
                continue

            self.last_player_data = player_data

            await self.write_message({'op': 0, 'event': 'PLAYER', 'data': player_data})
            await asyncio.sleep(1)

    async def send_position(self):

        position_data = {'position': self.player.position}
        await self.write_message({'op': 0, 'event': 'POSITION', 'data': position_data})

        self.last_position_data = position_data

        while True:

            position_data = {'position': self.player.position}

            if position_data == self.last_position_data:
                await asyncio.sleep(1)
                continue

            self.last_position_data = position_data

            await self.write_message({'op': 0, 'event': 'POSITION', 'data': position_data})


def setup(**kwargs):
    return [(r'/websocket', Websocket, kwargs)]
