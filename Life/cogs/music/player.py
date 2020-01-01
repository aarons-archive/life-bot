import asyncio

import discord
import granitepy

from cogs.music import queue
from utilities import utils


class Player(granitepy.Player):

    def __init__(self, bot, guild_id: int, node):
        super(Player, self).__init__(bot, guild_id, node)

        self.bot.loop.create_task(self.player_loop())

        self.queue = queue.Queue(bot)
        self.queue_loop = False
        self.channel = None

    async def player_loop(self):

        await self.bot.wait_until_ready()

        await self.set_volume(50)

        while True:
            try:
                if self.queue.size() == 0:
                    await self.bot.wait_for("queue_add", timeout=300.0)
                track = await self.queue.get_pos(0)

                await self.play(track)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild_id == self.guild_id)

                if self.queue_loop is True:
                    await self.queue.put(track)

                self.current = None

                continue

            except asyncio.TimeoutError:
                await self.channel.send("No tracks added for 5 minutes, Leaving the voice channel.")

                self.queue.clear()
                await self.destroy()

                break

    async def invoke_controller(self):

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
                                                f"`{utils.format_time(self.current.length / 1000)}`")
        embed.add_field(name="Queue looped:", value=f"`{self.queue_loop}`")
        embed.add_field(name="Queue Length:", value=f"`{str(self.queue.size())}`")
        embed.add_field(name="Requester:", value=self.current.requester.mention)
        embed.add_field(name="Paused:", value=f"`{self.paused}`")
        embed.add_field(name="Volume:", value=f"`{self.volume}%`")
        return await self.current.channel.send(embed=embed)
