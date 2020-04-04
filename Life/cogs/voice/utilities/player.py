import asyncio

import discord
import granitepy

from cogs.voice.utilities.queue import Queue
from cogs.voice.utilities import objects


class Player(granitepy.Player):

    def __init__(self, bot, node, guild):
        super().__init__(bot, node, guild)

        self.player_loop = self.bot.loop.create_task(self.player_loop())
        self.queue = Queue(bot, guild)
        self.queue_loop = False

    async def player_loop(self):

        while True:

            try:
                if self.queue.is_empty:
                    await self.bot.wait_for(f"{self.guild.id}_queue_add", timeout=300.0)

                track = await self.queue.get()

                if isinstance(track, objects.SpotifyTrack):
                    track = await self.get_result(ctx=track.ctx, query=track.title)
                    if not track:
                        continue

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
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{self.current.yt_id}/hqdefault.jpg")
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

    async def get_result(self, ctx, query: str):

        result = await self.node.get_tracks(query)
        if not result:
            return None

        if isinstance(result, granitepy.Playlist):
            result = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)
        else:
            result = objects.GraniteTrack(track_id=result[0].track_id, info=result[0].info, ctx=ctx)

        return result
