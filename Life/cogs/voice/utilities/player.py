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

import diorite
import discord
import spotify

from utilities import exceptions
from cogs.voice.utilities import objects, queue


class Player(diorite.Player):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.task = asyncio.create_task(self.loop())
        self.player_check = lambda guild_id: guild_id == self.guild.id

        self.queue = queue.LifeQueue(self)
        self.looping = False

        self.text_channel = kwargs.get('text_channel')

    @property
    def json(self):

        player_data = {
            'voice_channel_id': str(getattr(self.voice_channel, 'id', None)),
            'text_channel_id': str(getattr(self.text_channel, 'id', None)),
            'position': self.position,
            'looping': self.looping,
            'volume': self.volume,
            'paused': self.paused,
            'current': getattr(self.current, 'json', None),
            'queue': self.queue.json,
        }
        return json.dumps(player_data)

    @property
    def channel(self):
        return self.text_channel

    @property
    def is_paused(self):
        return 'Yes' if self.paused is True else 'No'

    @property
    def is_looping(self):
        return 'Yes' if self.looping is True else 'No'

    async def teardown(self):
        await self.destroy()
        self.task.cancel()

    async def invoke_controller(self, channel: discord.TextChannel):

        track = self.current

        embed = discord.Embed(title='Life bot music controller:', colour=self.bot.utils.guild_config(self.guild).colour)
        embed.set_thumbnail(url=track.thumbnail)
        embed.add_field(name=f'Now playing:', value=f'**[{track.title}]({track.uri})**', inline=False)
        embed.add_field(name='Requester:', value=f'{track.requester.mention}', inline=False)

        embed.add_field(name='Time:', value=f'`{self.bot.utils.format_time(round(self.position) / 1000)} / '
                                            f'{self.bot.utils.format_time(round(track.length) / 1000)}`')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name=f'Author', value=f'`{track.author}`')

        embed.add_field(name='Paused:', value=f'`{self.is_paused}`')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Queue looped:', value=f'`{self.is_looping}`')

        embed.add_field(name='Volume:', value=f'`{self.volume}%`')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Queue Length:', value=f'`{self.queue.size}`')

        return await channel.send(embed=embed)

    async def search(self, requester: discord.Member, search: str) -> objects.LifeSearch:

        spotify_url_regex = self.bot.spotify_url_regex.match(search)
        if spotify_url_regex is not None:

            source_type, source_id = spotify_url_regex.groups()
            try:
                if source_type == 'track':
                    result = await self.bot.spotify.get_track(source_id)
                    tracks = [result]
                elif source_type == 'album':
                    result = await self.bot.spotify.get_album(source_id)
                    tracks = await result.get_all_tracks()
                elif source_type == 'playlist':
                    result = spotify.Playlist(self.bot.spotify, await self.bot.spotify_http.get_playlist(source_id))
                    tracks = await result.get_all_tracks()
                else:
                    msg = f'The search `{search}` is a valid spotify URL but no tracks could be found for it'
                    raise exceptions.LifeVoiceError(msg)

            except spotify.NotFound:
                raise exceptions.LifeVoiceError(f'The search `{search}` is not a valid spotify URL.')

            spotify_tracks = []
            for track in tracks:
                track_info = {'identifier': track.id, 'isSeekable': True, 'author': track.artist.name or None,
                              'length': track.duration, 'isStream': False, 'position': 0, 'title': track.name,
                              'uri': track.url, 'thumbnail': track.images[0].url if track.images else None}
                track = objects.LifeTrack(track_id=track.id, info=track_info, requester=requester, source='spotify')
                spotify_tracks.append(track)

            return objects.LifeSearch(source='spotify', source_type=source_type, tracks=spotify_tracks, result=result)

        else:

            yt_search = search

            youtube_url_regex = self.bot.youtube_url_regex.match(search)
            if youtube_url_regex is None:
                yt_search = f'ytsearch:{search}'

            try:
                result = await self.node.get_tracks(query=yt_search)
            except diorite.TrackLoadError as error:
                raise exceptions.LifeVoiceError(f'The youtube search errored with level `{error.severity}`.\n'
                                                f'Reason: `{error.error_message}`')

            if result is None:
                raise exceptions.LifeVoiceError(f'The youtube search `{search}` found no tracks.')
            elif isinstance(result, diorite.Playlist):
                result = objects.LifePlaylist(playlist_info=result.playlist_info, tracks=result.raw_tracks,
                                              requester=requester, source='youtube')
                return objects.LifeSearch(source='youtube', source_type='playlist', result=result, tracks=result.tracks)
            else:
                result = [objects.LifeTrack(track_id=track.track_id, info=track.info,
                                            requester=requester, source='youtube') for track in result]
                return objects.LifeSearch(source='youtube', source_type='track', result=result, tracks=result)

    async def loop(self):

        while True:

            if self.queue.is_empty:
                try:
                    await self.bot.wait_for(f'life_queue_add', timeout=20.0, check=self.player_check)
                except asyncio.TimeoutError:
                    await self.teardown()
                    break

            track = await self.queue.get()

            if track.source == 'spotify':
                try:
                    search = await self.search(requester=track.requester, search=f'{track.author} - {track.title}')
                except exceptions.LifeVoiceError as error:
                    await self.channel.send(f'{error}')
                    continue
                else:
                    track = search.tracks[0]

            await self.play(track)

            try:
                await self.bot.wait_for('life_track_start', timeout=10.0, check=self.player_check)
            except asyncio.TimeoutError:
                await self.channel.send('Something went wrong while playing that track.')
                continue

            await self.invoke_controller(self.channel)

            await self.bot.wait_for('life_track_end', check=self.player_check)

            if self.looping is True and self.current is not None:
                self.queue.put(self.current)

            self.current = None
