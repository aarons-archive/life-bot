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

        self.queue = queue.LifeQueue(self)
        self.queue_loop = False

        self.text_channel = None

    @property
    def is_looping(self) -> bool:
        return self.queue_loop is True

    @property
    def channel(self) -> discord.TextChannel:
        return self.text_channel

    async def search(self, ctx: commands.Context, search: str) -> objects.LifeSearch:

        spotify_url_regex = self.bot.spotify_url_regex.match(search)
        if spotify_url_regex is not None:

            url_type, url_id = spotify_url_regex.groups()
            try:
                if url_type == 'track':
                    result = await self.bot.spotify.get_track(url_id)
                    tracks = [result]
                elif url_type == 'album':
                    result = await self.bot.spotify.get_album(url_id)
                    tracks = await result.get_all_tracks()
                elif url_type == 'playlist':
                    result = spotify.Playlist(self.bot.spotify, await self.bot.spotify_http.get_playlist(url_id))
                    tracks = await result.get_all_tracks()
                else:
                    raise exceptions.LifeVoiceError(f'The search `{search}` is a valid spotify URL but no tracks '
                                                    f'could be found for it')

                tracks = [objects.SpotifyTrack(ctx=ctx, info={'identifier': track.id,
                                                              'author': track.artist.name if track.artist else None,
                                                              'length': track.duration, 'title': track.name,
                                                              'uri': track.uri}) for track in tracks]
                return objects.LifeSearch(source='spotify', source_type=url_type, tracks=tracks, result=result)

            except spotify.NotFound:
                raise exceptions.LifeVoiceError(f'The search `{search}` is not a valid spotify URL.')

        else:

            youtube_url_regex = self.bot.youtube_url_regex.match(search)
            if youtube_url_regex is None:
                search = f'ytsearch:{search}'

            try:
                result = None
                for tries in range(3):
                    result = await self.node.get_tracks(query=search)
                    if not result:
                        await asyncio.sleep(5 * tries)
                        continue
                    else:
                        break

                if not result:
                    raise exceptions.LifeVoiceError(f'The search `{search}` found nothing.')
                elif isinstance(result, diorite.Playlist):
                    source_type = 'playlist'
                    result = objects.LifePlaylist(playlist_info=result.playlist_info, tracks=result.raw_tracks, ctx=ctx)
                    tracks = result.tracks
                else:
                    source_type = 'track'
                    result = [objects.LifeTrack(track_id=track.track_id, info=track.info, ctx=ctx) for track in result]
                    tracks = result

                return objects.LifeSearch(source='youtube', source_type=source_type, result=result, tracks=tracks)

            except diorite.TrackLoadError as e:
                raise exceptions.LifeVoiceError(f'There was a problem with your search: `{e.error_message}`')

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
                except exceptions.LifeVoiceError as e:
                    await self.channel.send(str(e))
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

            if self.is_looping:
                self.queue.put(self.current)

            self.current = None

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
