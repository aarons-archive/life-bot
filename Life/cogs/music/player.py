import asyncio

import andesite
import discord

from .queue import Queue
from ..utilities import formatting


class Player(andesite.Player):

    def __init__(self, bot, guild_id: int, node):
        super(Player, self).__init__(bot, guild_id, node)

        self.bot.loop.create_task(self.player_loop())
        self.queue = Queue(bot)

        self.queue_loop = False
        self.current = None
        self.channel = None
        self.track_channel = None
        self.paused = False
        self.volume = 50

    async def stop(self):
        # Over-ride the stop function so that it doesnt pause the player.
        # noinspection PyProtectedMember
        await self.node._websocket._send(op="stop", guildId=str(self.guild_id))

    async def player_loop(self):

        # Wait until the bot is ready.
        await self.bot.wait_until_ready()

        # Set default player values.
        await self.set_volume(self.volume)
        await self.set_pause(self.paused)

        # Start a loop.
        while True:

            try:
                if self.queue.size() == 0:
                    # Else, Wait for something to be added to the queue.
                    self.current = await self.bot.wait_for("queue_add", timeout=300.0)
                # If the queue is not empty get the first track.
                self.current = await self.queue.get_pos(0)

                # Set the channel for this track. (Each track has a channel but this is for timeouts where the current track will be None)
                self.track_channel = self.current.channel

                # Try to play the track.
                await self.play(self.current)

                # Wait for 0.5s then invoke the music controller. (The delay is so that that track can actually start playing)
                await asyncio.sleep(0.5)
                await self.invoke_controller()

                # Wait for the track to end.
                await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild_id == self.guild_id)

                # If the queue is looping, add the track back to the queue.
                if self.queue_loop is True:
                    await self.queue.put(self.current)

                # Set the current track to none. (So that commands dont think a track is still playing)
                self.current = None

                continue

            # If no track is added to the queue for 5 minutes, disconnect.
            except asyncio.TimeoutError:

                # If there is no current track channel, send the disconnect error to the original channel, else, send it to the track channel.
                if self.track_channel is None:
                    await self.channel.send("Leaving voice chat due to inactivity.")
                else:
                    await self.track_channel.send("Leaving voice chat due to inactivity.")

                # Clear the queue, disconnect and then destroy the player.
                self.queue.clear()
                await self.disconnect()
                await self.destroy()

            # Stop the loop if we get an error.
            break

    async def invoke_controller(self):

        embed = discord.Embed(
            title="Music controller:",
            colour=discord.Color.gold()
        )
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{self.current.yt_id}/hqdefault.jpg")
        embed.add_field(name=f"Now playing:", value=f"**[{self.current.title}]({self.current.uri})**", inline=False)
        if self.current.is_stream:
            embed.add_field(name="Time:", value="`Live stream`")
        else:
            embed.add_field(name="Time:", value=f"`{formatting.get_time(round(self.position) / 1000)}` / "
                                                f"`{formatting.get_time(self.current.length / 1000)}`")
        embed.add_field(name="Volume:", value=f"`{self.volume}%`")
        embed.add_field(name="Queue Length:", value=f"`{str(self.queue.size())}`")
        embed.add_field(name="Queue looped:", value=f"`{self.queue_loop}`")
        embed.add_field(name="Requester:", value=self.current.requester.mention)
        embed.add_field(name="Paused?", value=f"`{self.paused}`")
        return await self.current.channel.send(embed=embed)