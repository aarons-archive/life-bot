"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import json
import typing
from abc import ABC

from tornado.web import decode_signed_value

from cogs.dashboard.utilities import objects
from cogs.dashboard.utilities.bases import BaseWebsocketHandler
from cogs.voice.lavalink.objects import PlayerConnectedEvent, PlayerDisconnectedEvent, TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent
from utilities import exceptions


# noinspection PyAttributeOutsideInit
class Websocket(BaseWebsocketHandler, ABC):

    async def open(self) -> None:
        self.authenticated = False
        return await self.write_message({'op': 1, 'data': 'waiting for identify'})

    async def on_message(self, message) -> None:

        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            return self.close(code=4001, reason='invalid payload format. payloads must be json.')

        op = message.get('op')

        if op == 0:  # DISPATCH
            return self.close(code=4002, reason='invalid op code. code 0 "DISPATCH" is receive only.')
        elif op == 1:  # HELLO
            return self.close(code=4002, reason='invalid op code. code 1 "HELLO" is receive only.')

        elif op == 2:  # IDENTIFY

            if self.authenticated is True:
                return self.close(code=4005, reason='already authenticated.')

            data = message.get('data')

            guild = self.bot.get_guild(int(data.get('guild_id')))
            if not guild:
                return self.close(code=4004, reason='invalid guild id.')

            identifier = decode_signed_value(secret=self.application.settings["cookie_secret"], name='identifier', value=data.get('identifier').strip('"'))
            if identifier is None:
                identifier = data.get('identifier')

            token_response = await self.bot.redis.hget('tokens', identifier)
            if not token_response:
                return self.close(code=4003, reason='not logged in. must log in with discord on the site at least once.')

            token_response = objects.TokenResponse(data=json.loads(token_response.decode()))
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

            self.authenticated = True
            self.guild = guild

            self.ready_task = asyncio.create_task(self.send_ready())
            self.position_task = asyncio.create_task(self.send_position())

            self.bot.add_listener(self.handle_event, 'on_lavalink_track_start')
            self.bot.add_listener(self.handle_event, 'on_lavalink_track_end')
            self.bot.add_listener(self.handle_event, 'on_lavalink_track_exception')
            self.bot.add_listener(self.handle_event, 'on_lavalink_track_stuck')
            self.bot.add_listener(self.handle_event, 'on_lavalink_player_connected')
            self.bot.add_listener(self.handle_event, 'on_lavalink_player_disconnected')

        elif self.authenticated is False:
            return self.close(code=4006, reason='not authorized.')

    async def handle_event(self, event) -> None:

        if not event.player.guild.id == self.guild.id:
            return

        if isinstance(event, PlayerConnectedEvent):
            return await self.send_connected()
        elif isinstance(event, PlayerDisconnectedEvent):
            return await self.send_disconnected()
        elif isinstance(event, TrackStartEvent):
            return await self.send_track_start()
        elif isinstance(event, TrackEndEvent):
            return await self.send_track_end()

    async def send_ready(self) -> None:

        self.ready = False

        while True:

            if not self.guild.voice_client:
                self.ready = False
                await asyncio.sleep(5)
                continue

            if self.ready:
                await asyncio.sleep(5)
                continue

            data = {
                'voice_channel_id': str(getattr(self.guild.voice_client.channel, 'id', None)),
                'text_channel_id': str(getattr(self.guild.voice_client.text_channel, 'id', None)),
                'is_connected': self.guild.voice_client.is_connected,
                'is_playing': self.guild.voice_client.is_playing,
                'is_paused': self.guild.voice_client.is_paused,
                'position': self.guild.voice_client.position,
                'volume': self.guild.voice_client.volume,
                'current': getattr(self.guild.voice_client.current, 'json', None),
                'queue': self.guild.voice_client.queue.json
            }
            await self.write_message({'op': 0, 'event': 'READY', 'data': data})
            self.ready = True

    async def send_connected(self) -> None:

        data = {
            'voice_channel_id': str(getattr(self.guild.voice_client.channel, 'id', None)),
            'text_channel_id': str(getattr(self.guild.voice_client.text_channel, 'id', None)),
            'is_connected': self.guild.voice_client.is_connected,
            'is_playing': self.guild.voice_client.is_playing,
            'is_paused': self.guild.voice_client.is_paused,
            'position': self.guild.voice_client.position,
            'volume': self.guild.voice_client.volume,
            'current': getattr(self.guild.voice_client.current, 'json', None),
            'queue': self.guild.voice_client.queue.json
        }
        await self.write_message({'op': 0, 'event': 'CONNECTED', 'data': data})

    async def send_disconnected(self) -> None:
        await self.write_message({'op': 0, 'event': 'DISCONNECTED'})

    async def send_track_start(self) -> None:

        data = {
            "current": getattr(self.guild.voice_client.current, 'json', None)
        }
        await self.write_message({'op': 0, 'event': 'TRACK_START', 'data': data})

    async def send_track_end(self) -> None:
        await self.write_message({'op': 0, 'event': 'TRACK_END'})

    async def send_position(self) -> None:

        while True:

            if not self.guild.voice_client:
                await asyncio.sleep(1)
                continue

            position_data = {
                'position': self.guild.voice_client.position,
                'length': getattr(self.guild.voice_client.current, 'length', 0)
            }

            await self.write_message({'op': 0, 'event': 'POSITION', 'data': position_data})
            await asyncio.sleep(0.5)


def setup(**kwargs):
    return [(r'/websocket', Websocket, kwargs)]
