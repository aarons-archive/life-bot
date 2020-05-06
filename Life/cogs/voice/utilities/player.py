import asyncio

import discord
import granitepy
import spotify
from discord.ext import commands

from cogs.utilities import exceptions
from cogs.voice.utilities import objects
from cogs.voice.utilities.queue import Queue


class Player(granitepy.Player):

    def __init__(self, node, guild):
        super().__init__(node, guild)

        self.player_loop = self.bot.loop.create_task(self.player_loop())
        self.queue = Queue(self.bot, self.guild)

        self.queue_loop = False
        self.use_text_channel = True
        self.text_channel = None
        
    @property
    def channel(self):
        if self.use_text_channel is True:
            return self.text_channel
        else:
            return self.current.channel if self.current is not None else self.text_channel

    @property
    def is_looping(self):
        return self.queue_loop is True

    async def player_loop(self):

        while True:

            try:
                if self.queue.is_empty:
                    await self.bot.wait_for(f'{self.guild.id}_queue_add', timeout=300.0)

                track = await self.queue.get()

                if isinstance(track, objects.SpotifyTrack):
                    result = await self.get_results(ctx=track.ctx, search=f'{track.title} - {track.author}')
                    if not result:
                        continue
                    track = result['tracks'][0]

                await self.play(track)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                await self.bot.wait_for('granitepy_track_end', check=lambda p: p.player.guild.id == self.guild.id)

                if self.is_looping is True:
                    self.queue.put(self.current)

                self.current = None

            except asyncio.TimeoutError:

                await self.channel.send('No tracks have been added to the queue for '
                                        'over 5 minutes, leaving the voice channel.')
                self.queue.clear()
                self.player_loop.cancel()
                return await self.destroy()

    async def invoke_controller(self):

        if self.current is None:
            return await self.channel.send('There is nothing currently playing, seeing '
                                            'this usually means something broke.')

        embed = discord.Embed(title='Life bot music controller:', colour=discord.Color.gold())
        embed.set_thumbnail(url=f'https://img.youtube.com/vi/{self.current.identifier}/maxresdefault.jpg')
        embed.add_field(name=f'Now playing:', value=f'**[{self.current.title}]({self.current.uri})**', inline=False)
        embed.add_field(name='Requester:', value=f'{self.current.requester.mention}', inline=False)


        embed.add_field(name='Time:', value=f'`{self.bot.utils.format_time(round(self.position) / 1000)} / '
                                            f'{self.bot.utils.format_time(round(self.current.length) / 1000)}`')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name=f'Author', value=f'`{self.current.author}`')

        embed.add_field(name='Paused:', value=f'`{self.paused}`')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Queue looped:', value=f'`{self.queue_loop}`')

        embed.add_field(name='Volume:', value=f'`{self.volume}%`')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Queue Length:', value=f'`{self.queue.size}`')

        return await self.channel.send(embed=embed)

    async def get_results(self, ctx: commands.Context, search: str):

        spotify_url = self.bot.spotify_url_regex.match(search)
        if spotify_url is not None:

            spotify_type, spotify_id = spotify_url.groups()

            try:
                if spotify_type == 'track':
                    result = await self.bot.spotify.get_track(spotify_id)
                    spotify_tracks = [result]
                elif spotify_type == 'album':
                    result = await self.bot.spotify.get_album(spotify_id)
                    spotify_tracks = await result.get_all_tracks()
                elif spotify_type == 'playlist':
                    result = spotify.Playlist(self.bot.spotify, await self.bot.http_spotify.get_playlist(spotify_id))
                    spotify_tracks = await result.get_all_tracks()
                else:
                    raise exceptions.LifeVoiceError(f'The spotify link `{search}` is not a valid '
                                                    f'spotify track, album or playlist link.')
            except spotify.HTTPException:
                raise exceptions.LifeVoiceError(f'The link `{search}` is a spotify link however no '
                                                f'tracks, albums or playlists could be found that match it.')
            if not spotify_tracks:
                raise exceptions.LifeVoiceError(f'The link `{search}` is a spotify link however no '
                                                f'tracks, albums or playlists could be found that match it.')

            tracks = [objects.SpotifyTrack(ctx=ctx, title=f'{track.name}', author=f'{track.artist.name}',
                                           length=track.duration, uri=track.url) for track in spotify_tracks]
            return {'type': 'spotify', 'tracks': tracks, 'result': result}

        else:

            result = await self.get_tracks(query=f'{search}')
            if not result:
                raise exceptions.LifeVoiceError(f'The youtube search `{search}` returned nothing.')

            if isinstance(result, granitepy.Playlist):
                result = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)
                tracks = result.tracks
            elif isinstance(result[0], granitepy.Track):
                result = [objects.GraniteTrack(track_id=track.track_id, info=track.info, ctx=ctx) for track in result]
                tracks = [result[0]]
            else:
                raise exceptions.LifeVoiceError(f'There was some kind of error while searching for tracks, '
                                                f'join my support server for more information/help.')

            return {'type': 'youtube', 'tracks': tracks, 'result': result}
