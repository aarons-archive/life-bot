import asyncio

import discord
import granitepy

from utilities.queue import Queue
from utilities import utils


class Player(granitepy.Player):

    def __init__(self, bot, node, guild):
        super().__init__(bot, node, guild)

        self.player_loop = self.bot.loop.create_task(self.player_loop())
        self.queue = Queue(bot, guild)
        self.queue_loop = False

    async def player_loop(self):

        while True:

            try:
                # If the queue is empty, wait for something to be added to it.
                if self.queue.is_empty:
                    await self.bot.wait_for(f"{self.guild.id}_queue_add", timeout=300.0)

                # Get the first track in the queue.
                track = await self.queue.get()

                # Play the track and invoke the controller.
                await self.play(track)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                # Wait for the track to finish playing.
                await self.bot.wait_for("granitepy_track_end", check=lambda p: p.player.guild.id == self.guild.id)

                # If the queue is looping, add the track back to it.
                if self.queue_loop is True:
                    await self.queue.put(self.current)

                # Set the current track to None
                self.current = None

            # If we are waiting for a track for more than 5 minutes, notify channel and destroy player.
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
        embed.add_field(name="Time:", value=f"`{utils.format_time(round(self.position) / 1000)}` / "
                                            f"`{utils.format_time(round(self.current.length) / 1000)}`")
        embed.add_field(name="Queue looped:", value=f"`{self.queue_loop}`")
        embed.add_field(name="Queue Length:", value=f"`{str(self.queue.size)}`")
        embed.add_field(name="Requester:", value=self.current.requester.mention)
        embed.add_field(name="Paused:", value=f"`{self.paused}`")
        embed.add_field(name="Volume:", value=f"`{self.volume}%`")

        if self.text_channel:
            return await self.text_channel.send(embed=embed)
        else:
            return await self.current.channel.send(embed=embed)
