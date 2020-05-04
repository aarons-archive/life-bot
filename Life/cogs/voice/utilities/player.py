import asyncio
import re

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
        self.text_channel = None

    async def player_loop(self):

        while True:

            try:
                if self.queue.is_empty:
                    await self.bot.wait_for(f"{self.guild.id}_queue_add", timeout=300.0)

                track = await self.queue.get()

                if isinstance(track, objects.SpotifyTrack):
                    track = await self.get_results(ctx=track.ctx, search=f"{track.title} - {track.author}")
                    if not track:
                        continue
                    track = track["tracks"][0]

                await self.play(track)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                await self.bot.wait_for("granitepy_track_end", check=lambda p: p.player.guild.id == self.guild.id)

                if self.queue_loop is True:
                    self.queue.put(self.current)

                self.current = None

            except asyncio.TimeoutError:

                await self.text_channel.send("No tracks added for 5 minutes, Leaving the voice channel.")

                self.queue.clear()
                self.player_loop.cancel()
                await self.destroy()

    async def invoke_controller(self):

        if self.current is None:
            return

        embed = discord.Embed(
            title="Music controller:",
            colour=discord.Color.gold()
        )
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{self.current.identifier}/hqdefault.jpg")
        embed.add_field(name=f"Now playing:", value=f"**[{self.current.title}]({self.current.uri})**", inline=False)
        embed.add_field(name="Time:", value=f"`{self.bot.utils.format_time(round(self.position) / 1000)}` / "
                                            f"`{self.bot.utils.format_time(round(self.current.length) / 1000)}`")
        embed.add_field(name="Queue looped:", value=f"`{self.queue_loop}`")
        embed.add_field(name="Queue Length:", value=f"`{str(self.queue.size)}`")
        embed.add_field(name="Requester:", value=self.current.requester.mention)
        embed.add_field(name="Paused:", value=f"`{self.paused}`")
        embed.add_field(name="Volume:", value=f"`{self.volume}%`")

        if self.text_channel:
            return await self.text_channel.send(embed=embed)
        else:
            return await self.current.channel.send(embed=embed)

    async def get_results(self, ctx: commands.Context, search: str):

        spotify_regex = re.compile("https://open.spotify.com?.+(album|playlist|track)/([a-zA-Z0-9]+)").match(search)
        if spotify_regex:
            
            spotify_type, spotify_id = spotify_regex.groups()
            
            try:
                if spotify_type == "track":
                    result = await self.bot.spotify.get_track(spotify_id)
                    spotify_tracks = [result]
                elif spotify_type == "album":
                    result = await self.bot.spotify.get_album(spotify_id)
                    spotify_tracks = await result.get_all_tracks()
                elif spotify_type == "playlist":
                    result = spotify.Playlist(self.bot.spotify, await self.bot.http_spotify.get_playlist(spotify_id))
                    spotify_tracks = await result.get_all_tracks()
                else:
                    raise exceptions.LifeVoiceError(f"The spotify link `{search}` is not a valid spotify track/album/playlist link.")
            except spotify.HTTPException:
                raise exceptions.LifeVoiceError(f"The spotify link `{search}` is not a valid spotify track/album/playlist link.")
    
            if not spotify_tracks:
                raise exceptions.LifeVoiceError(f"No spotify tracks were found for the search `{search}`")
    
            tracks = [objects.SpotifyTrack(ctx=ctx, title=f"{track.name}", author=f"{track.artist.name}", length=track.duration, uri=track.url) for track in spotify_tracks]
            return {"type": "spotify", "tracks": tracks, "result": result}
                    
        else:
            
            result = await self.get_tracks(query=f"{search}")
            if not result:
                raise exceptions.LifeVoiceError(f"No youtube tracks were found for the search `{search}`")
                
            if isinstance(result, granitepy.Playlist):
                result = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)
                tracks = result.tracks
            elif isinstance(result[0], granitepy.Track):
                result = [objects.GraniteTrack(track_id=track.track_id, info=track.info, ctx=ctx) for track in result]
                tracks = [result[0]]
            else:
                raise exceptions.LifeVoiceError(f"There was an error while searching for tracks.")
                    
            return {"type": "youtube", "tracks": tracks, "result": result}
