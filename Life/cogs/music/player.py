import asyncio

import discord

import granitepy
from .queue import Queue
from ..utilities import formatting


class Player(granitepy.Player):

    def __init__(self, bot, guild_id: int, node):
        super(Player, self).__init__(bot, guild_id, node)

        self.bot.loop.create_task(self.player_loop())

        self.queue = Queue(bot)
        self.queue_loop = False

    async def player_loop(self):

        await self.bot.wait_until_ready()

        # Set player default values
        await self.set_volume(50)

        while True:

            try:
                # If the queue is empty, wait for something to be added.
                if self.queue.size() == 0:
                    await self.bot.wait_for("queue_add", timeout=300.0)

                # If the queue was not empty or something was added, get it.
                track = await self.queue.get_pos(0)

                # Play the track.
                await self.play(track)

                # Wait for 0.5s then invoke the music controller. (The delay is so that that the track can actually start playing)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                # Wait for the track end event.
                await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild_id == self.guild_id)

                # If the queue is looping, add this track back to the queue.
                if self.queue_loop is True:
                    await self.queue.put(track)

                # Set the current track to none. (So that commands dont think a track is still playing)
                self.current = None

                # Continue looping.
                continue

            # If no track is added to the queue for 5 minutes, disconnect.
            except asyncio.TimeoutError:

                print("Timeout errror")

                # Clear the queue, disconnect and then destroy the player.
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
            embed.add_field(name="Time:", value=f"`{formatting.get_time(round(self.position) / 1000)}` / "
                                                f"`{formatting.get_time(self.current.length / 1000)}`")
        embed.add_field(name="Queue looped:", value=f"`{self.queue_loop}`")
        embed.add_field(name="Queue Length:", value=f"`{str(self.queue.size())}`")
        embed.add_field(name="Requester:", value=self.current.requester.mention)
        embed.add_field(name="Paused:", value=f"`{self.paused}`")
        embed.add_field(name="Volume:", value=f"`{self.volume}%`")
        return await self.current.channel.send(embed=embed)