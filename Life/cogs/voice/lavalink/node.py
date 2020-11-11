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

import re
import typing
from urllib import parse

import aiohttp
import spotify
import yarl

from cogs.voice.lavalink import objects
from cogs.voice.lavalink.exceptions import *
from cogs.voice.lavalink.player import Player
from utilities import context, exceptions


class Node:

    def __init__(self, *, client, host: str, port: str, password: str, identifier: str) -> None:

        self.client = client
        self.host = host
        self.port = port
        self.password = password
        self.identifier = identifier

        self.websocket = None
        self.stats = None
        self.task = None

        self.players: typing.Dict[int, Player] = {}

        self.spotify_url_regex = re.compile(r'https?://open.spotify.com/(album|playlist|track)/([a-zA-Z0-9]+)')

    def __repr__(self) -> str:
        return f'<LavaLinkNode identifier=\'{self.identifier}\' player_count={len(self.players)}>'

    @property
    def headers(self) -> dict:
        return {
            'Authorization': self.password,
            'Num-Shards': str(self.client.bot.shard_count or 1),
            'User-Id': str(self.client.bot.user.id)
        }

    @property
    def rest_url(self) -> str:
        return f'http://{self.host}:{self.port}/'

    @property
    def ws_url(self) -> str:
        return f'ws://{self.host}:{self.port}/'

    @property
    def is_connected(self) -> bool:
        return self.websocket is not None and not self.websocket.closed

    async def connect(self) -> None:

        await self.client.bot.wait_until_ready()

        try:
            websocket = await self.client.session.ws_connect(self.ws_url, headers=self.headers)

        except Exception as error:

            if isinstance(error, aiohttp.WSServerHandshakeError):
                if error.status == 401:
                    raise NodeCreationError(f'Node \'{self.identifier}\' has invalid authorization.')
            else:
                raise NodeCreationError(f'Node \'{self.identifier}\' was unable to connect. Reason: {error}')

        else:

            self.websocket = websocket
            self.client.nodes[self.identifier] = self

            self.task = self.client.bot.loop.create_task(self.listen())

    async def disconnect(self) -> None:

        for player in self.players.copy().values():
            await player.destroy()

        if self.is_connected:
            await self.websocket.close()

        self.task.cancel()

    async def destroy(self) -> None:

        await self.disconnect()
        del self.client.nodes[self.identifier]

    async def listen(self) -> None:

        while True:

            message = await self.websocket.receive()

            if message.type is aiohttp.WSMsgType.CLOSED:
                await self.disconnect()
                raise NodeConnectionError(f'Node \'{self.identifier}\' has closed. Reason: {message.extra}')

            else:

                message = message.json()

                op = message.pop('op', None)
                if not op:
                    continue

                if op == 'stats':
                    self.stats = objects.Stats(node=self, stats=message)

                elif op == 'event':

                    player = self.players.get(int(message.pop('guildId')))
                    if not player:
                        continue

                    try:
                        track = await self.decode_track(track_id=message.pop('track'))
                    except exceptions.VoiceError:
                        pass
                    else:
                        message['track'] = track

                    message['player'] = player
                    player.dispatch_event(data=message)

                elif op == 'playerUpdate':

                    player = self.players.get(int(message.pop('guildId')))
                    if not player:
                        continue

                    await player.update_state(data=message)

                else:
                    continue

    async def send(self, **data) -> None:

        if not self.is_connected:
            raise NodeConnectionError(f'Node \'{self.identifier}\' is not connected.')

        await self.websocket.send_json(data)

    async def decode_track(self, *, track_id: str, ctx: context.Context = None) -> objects.Track:

        async with self.client.session.get(f'{self.rest_url}/decodetrack?', headers={'Authorization': self.password}, params={'track': track_id}) as response:
            data = await response.json()

            if not response.status == 200:
                raise exceptions.VoiceError('Track id was not valid.')

        return objects.Track(track_id=track_id, info=data, ctx=ctx)

    async def search(self, *, query: str, raw: bool = False, ctx: context.Context = None) -> objects.Search:

        spotify_check = self.spotify_url_regex.match(query)
        if spotify_check is not None:

            spotify_type, spotify_id = spotify_check.groups()
            return await self.spotify_search(query=query, spotify_type=spotify_type, spotify_id=spotify_id, ctx=ctx)

        url_check = yarl.URL(query)
        if url_check.scheme is not None and url_check.host is not None:
            return await self.lavalink_search(query=query, ctx=ctx, raw=raw)

        if query.startswith('soundcloud'):
            return await self.lavalink_search(query=f'scsearch:{query[11:]}', ctx=ctx, raw=raw)

        return await self.lavalink_search(query=f'ytsearch:{query}', ctx=ctx, raw=raw)

    async def lavalink_search(self, *, query: str, raw: bool = False, ctx: context.Context = None) -> objects.Search:

        async with self.client.session.get(url=f'{self.rest_url}/loadtracks?identifier={parse.quote(query)}', headers={'Authorization': self.password}) as response:
            data = await response.json()

        if raw is True:
            return data

        load_type = data.pop('loadType')

        if load_type == 'LOAD_FAILED':
            exception = data.get("exception")
            raise exceptions.VoiceError(f'There was an error of severity `{exception.get("severity")}` while loading tracks. Reason: `{exception.get("message")}`')

        elif load_type == 'NO_MATCHES':
            raise exceptions.VoiceError(f'The query `{query}` returned no tracks.')

        elif load_type == 'PLAYLIST_LOADED':
            playlist = objects.Playlist(playlist_info=data.get('playlistInfo'), raw_tracks=data.get('tracks'), ctx=ctx)
            return objects.Search(source=playlist.tracks[0].source, source_type='playlist', tracks=playlist.tracks, result=playlist)

        elif load_type == 'SEARCH_RESULT' or load_type == 'TRACK_LOADED':

            raw_tracks = data.get('tracks')
            if not raw_tracks:
                raise exceptions.VoiceError(f'The query `{query}` returned no tracks.')

            tracks = [objects.Track(track_id=track.get('track'), info=track.get('info'), ctx=ctx) for track in raw_tracks]
            return objects.Search(source=tracks[0].source, source_type='track', tracks=tracks, result=tracks)

    async def spotify_search(self, *, query: str, spotify_type: str, spotify_id: str, ctx: context.Context = None) -> objects.Search:

        try:
            if spotify_type == 'track':
                result = await self.client.bot.spotify.get_track(spotify_id)
                spotify_tracks = [result]
            elif spotify_type == 'album':
                result = await self.client.bot.spotify.get_album(spotify_id)
                spotify_tracks = await result.get_tracks(limit=100)
            elif spotify_type == 'playlist':
                result = spotify.Playlist(self.client.bot.spotify, await self.client.bot.spotify_http.get_playlist(spotify_id))
                spotify_tracks = await result.get_all_tracks()
            else:
                raise exceptions.VoiceError(f'The query `{query}` is not a valid spotify URL.')

        except spotify.NotFound:
            raise exceptions.VoiceError(f'The query `{query}` is not a valid spotify URL.')

        if not spotify_tracks:
            raise exceptions.VoiceError(f'The query `{query}` is a valid spotify URL however no tracks could be found for it.')

        tracks = []
        for track in spotify_tracks:

            info = {'identifier': track.id, 'isSeekable': False, 'author': ', '.join([artist.name for artist in track.artists]), 'length': track.duration,
                    'isStream': False, 'position': 0, 'title': track.name, 'uri': track.url if track.url else 'spotify',
                    'thumbnail': track.images[0].url if track.images else None
                    }
            tracks.append(objects.Track(track_id='', info=info, ctx=ctx))

        return objects.Search(source='spotify', source_type=spotify_type, tracks=tracks, result=result)

