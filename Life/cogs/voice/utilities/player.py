import asyncio

import diorite
import discord
import spotify
from discord.ext import commands

from cogs.utilities import exceptions
from cogs.voice.utilities import objects, queue


class Player(diorite.Player):

    def __init__(self, node: diorite.Node, guild: discord.Guild):
        super().__init__(node, guild)

        self.task = self.bot.loop.create_task(self.player_loop())
        self.check = lambda guild_id: guild_id == self.guild.id

        self.text_channel = None

        self.queue = queue.LifeQueue(self)
        self.queue_loop = False

    @property
    def channel(self) -> discord.TextChannel:
        return self.text_channel

    @property
    def is_looping(self) -> str:
        return 'Yes' if self.queue_loop is True else 'No'

    @property
    def is_paused(self) -> str:
        return 'Yes' if self.paused is True else 'No'

    async def search(self, ctx: commands.Context, search: str) -> objects.LifeSearch:

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
                author = track.artist.name if track.artist else None
                images = track.images[0].url if track.images else None
                track_info = {'identifier': track.id, 'author': author, 'length': track.duration,
                              'title': track.name, 'uri': track.url, 'thumbnail': images}
                spotify_tracks.append(objects.SpotifyTrack(ctx=ctx, info=track_info))

            return objects.LifeSearch(source='spotify', source_type=source_type, tracks=spotify_tracks, result=result)

        else:

            youtube_url_regex = self.bot.youtube_url_regex.match(search)
            if youtube_url_regex is None:
                yt_search = f'ytsearch:{search}'
            else:
                yt_search = search

            result = None
            for tries in range(5):
                try:
                    result = await self.node.get_tracks(query=yt_search)
                    if result:
                        break
                except diorite.TrackLoadError:
                    pass

                await asyncio.sleep(3 * tries)
                continue

            if result is None:
                raise exceptions.LifeVoiceError(f'The youtube search `{search}` found no tracks.')
            elif isinstance(result, diorite.Playlist):
                result = objects.LifePlaylist(playlist_info=result.playlist_info, tracks=result.raw_tracks, ctx=ctx)
                return objects.LifeSearch(source='youtube', source_type='playlist', result=result, tracks=result.tracks)
            else:
                result = [objects.LifeTrack(track_id=track.track_id, info=track.info, ctx=ctx) for track in result]
                return objects.LifeSearch(source='youtube', source_type='track', result=result, tracks=result)

    async def invoke_controller(self, track: objects.LifeTrack):

        await asyncio.sleep(0.5)

        embed = discord.Embed(title='Life bot music controller:', colour=discord.Color.gold())
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

        await self.channel.send(embed=embed)

    async def player_loop(self):

        while True:

            if self.queue.is_empty:
                try:
                    await self.bot.wait_for(f'life_queue_add', timeout=300.0, check=self.check)
                except asyncio.TimeoutError:
                    await self.destroy()
                    self.task.cancel()

            track = await self.queue.get()
            if isinstance(track, objects.SpotifyTrack):
                try:
                    search = await self.search(ctx=track.ctx, search=f'{track.author} - {track.title}')
                except exceptions.LifeVoiceError as error:
                    await self.channel.send(f"{error}")
                    continue
                else:
                    track = search.tracks[0]

            self.current = track
            await self.play(self.current)
            try:
                await self.bot.wait_for('life_track_start', timeout=10.0, check=self.check)
            except asyncio.TimeoutError:
                await self.channel.send('Something went wrong while playing that track.')
                continue

            await self.invoke_controller(self.current)
            await self.bot.wait_for('life_track_end', check=self.check)

            if self.queue_loop is True:
                self.queue.put(self.current)

            self.current = None
