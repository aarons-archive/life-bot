import asyncio

import discord
import granitepy

from cogs.music import queue
from utilities import utils


class Player(granitepy.Player):

    def __init__(self, bot, node, guild):
        super().__init__(bot, node, guild)

        self.player_loop = self.bot.loop.create_task(self.player_loop())
        self.queue = queue.Queue(bot)
        self.queue_loop = False

    async def player_loop(self):

        await self.bot.wait_until_ready()

        while True:
            try:

                if self.queue.size == 0:
                    await self.bot.wait_for("queue_add", timeout=300.0)
                track = await self.queue.get()

                await self.play(track)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild.id == self.guild.id)

                if self.queue_loop is True:
                    await self.queue.put(self.current)

                self.current = None

            except asyncio.TimeoutError:

                try:
                    await self.text_channel.send("No tracks added for 5 minutes, Leaving the voice channel.")
                except discord.Forbidden:
                    pass

                await self.destroy()
                self.queue.clear()
                self.player_loop.cancel()

    async def invoke_controller(self):

        if self.current is None:
            return

        embed = discord.Embed(
            title="Music controller:",
            colour=discord.Color.gold()
        )
        embed.set_image(url=f"https://img.youtube.com/vi/{self.current.yt_id}/hqdefault.jpg")
        embed.add_field(name=f"Now playing:", value=f"**[{self.current.title}]({self.current.uri})**", inline=False)
        if self.current.is_stream:
            embed.add_field(name="Time:", value="`Live stream`")
        else:
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
