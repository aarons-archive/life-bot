import asyncio

import discord
import spotify
from discord.ext import commands

import diorite
from cogs.utilities import exceptions
from cogs.voice.utilities import objects, queue


class Player(diorite.Player):

    def __init__(self, node, guild):
        super().__init__(node, guild)

        self.task = self.bot.loop.create_task(self.player_loop())
        self.check = lambda guild_id: guild_id == self.guild.id

        self.queue = queue.LifeQueue(self)
        self.queue_loop = False

        self.text_channel = None

    @property
    def channel(self):
        return self.text_channel

    @property
    def is_looping(self):
        return self.queue_loop is True

    async def player_loop(self):

        while True:

            # If the queue is empty, wait for something to be added. Timeout and destroy player after 10 minutes.
            if self.queue.is_empty:
                try:
                    await self.bot.wait_for(f"life_queue_add", timeout=600.0, check=self.check)

                except asyncio.TimeoutError:
                    await self.channel.send("No tracks have been added to the queue for over 10 minutes, "
                                            "disconnecting.")
                    await self.destroy()
                    self.queue.clear()
                    self.task.cancel()

            # Get a track from the queue, if it was a spotify track, search for it on youtube.
            track = await self.queue.get()
            if isinstance(track, objects.SpotifyTrack):
                try:
                    search = await self.search(ctx=track.ctx, search=f"{track.title} - {track.author}")
                except exceptions.LifeVoiceError as e:
                    await self.channel.send(e)
                    continue
                else:
                    track = search['result'][0]

            # Play and wait for the track to start, if there's an error, an event should catch it so we can skip
            self.current = track
            await self.play(track)
            try:
                await self.bot.wait_for("life_track_start", timeout=5.0, check=self.check)
            except asyncio.TimeoutError:
                continue

            # If we are now playing the track, lets invoke the controller.
            await self.invoke_controller(self.current)

            # Wait for our end event to be dispatched by custom listeners, then continue the loop.
            await self.bot.wait_for("life_track_end", check=self.check)

            if self.is_looping:
                self.queue.put(self.current)

            self.current = None

    async def search(self, ctx: commands.Context, search: str):

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
                    raise exceptions.LifeVoiceError(f'The spotify link `{search}` is not a valid spotify track, album '
                                                    f'or playlist link.')
            except spotify.HTTPException:
                raise exceptions.LifeVoiceError(f'The link `{search}` is a spotify link however no tracks, albums or '
                                                f'playlists that match it could be found.')
            if not spotify_tracks:
                raise exceptions.LifeVoiceError(f'The link `{search}` is a spotify link however no tracks, albums or '
                                                f'playlists that match it could be found.')

            tracks = [objects.SpotifyTrack(ctx=ctx, title=f'{track.name}', author=f'{track.artist.name}',
                                           length=track.duration, uri=track.url) for track in spotify_tracks]
            return {'type': 'spotify', 'return_type': spotify_type, 'result': result, 'tracks': tracks}

        else:

            youtube_url = self.bot.youtube_url_regex.match(search)
            if youtube_url is None:
                search = f"ytsearch:{search}"

            try:

                result = await self.node.get_tracks(query=f'{search}')

                if isinstance(result, diorite.Playlist):
                    return_type = "playlist"
                    result = objects.LifePlaylist(playlist_info=result.playlist_info, tracks=result.raw_tracks, ctx=ctx)
                elif isinstance(result, list) and isinstance(result[0], diorite.Track):
                    return_type = "track"
                    result = [objects.LifeTrack(track_id=track.track_id, info=track.info, ctx=ctx) for track in result]
                else:
                    raise exceptions.LifeVoiceError(f'The youtube search `{search}` returned nothing.')

            except diorite.TrackLoadError as e:
                raise exceptions.LifeVoiceError(f"There was a problem while loading your search: `{e.error_message}`")

            return {'type': 'youtube', 'return_type': return_type, 'result': result}

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
