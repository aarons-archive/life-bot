import asyncio

import andesite
import discord

from .queue import Queue
from ..utilities import formatting


class Player(andesite.Player):

    def __init__(self, bot, guild_id: int, node):
        super(Player, self).__init__(bot, guild_id, node)

        self.bot.loop.create_task(self.player_loop())
        self.queue = Queue()

        self.queue_loop = False
        self.current = None
        self.paused = False
        self.volume = 50

    # Over-ride the stop function so that it doesnt pause the player.
    async def stop(self):
        # noinspection PyProtectedMember
        await self.node._websocket._send(op="stop", guildId=str(self.guild_id))

    async def player_loop(self):

        # Wait until the bot is ready.
        await self.bot.wait_until_ready()

        # Set player defaults.
        await self.set_volume(self.volume)
        await self.set_pause(self.paused)

        # Start a player loop.
        while True:
            # Get the first track in the queue.
            track = await self.queue.get_pos(0)

            # If one was not found, continue
            if not track:
                continue

            # Set the current track to this track.
            self.current = track

            # Try to play the track, accept TrackStuck errors.
            try:
                await self.play(track)
            except andesite.TrackStuckEvent:
                self.current.channel.send("The current track has broken.")

            # Invoke the controller.
            await asyncio.sleep(0.4)
            await self.invoke_controller()

            # Wait for the end of the track.
            await self.bot.wait_for("andesite_track_end", check=lambda p: p.player.guild_id == self.guild_id)

            # If the queue is looping, add the track back to the queue.
            if self.queue_loop is True:
                await self.queue.put(self.current)

            # Set the current song back to None.
            self.current = None

    async def invoke_controller(self):

        embed = discord.Embed(
            title="Music controller:",
            colour=discord.Color.gold()
        )
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{self.current.yt_id}/maxresdefault.jpg")
        embed.add_field(name=f"Now playing:", value=f"**[{self.current.title}]({self.current.uri})**", inline=False)
        if self.current.is_stream:
            embed.add_field(name="Time:", value="`Live stream`")
        else:
            embed.add_field(name="Time:", value=f"`{formatting.get_time(round(self.position) / 1000)}` / "
                                                f"`{formatting.get_time(self.current.length / 1000)}`")
        embed.add_field(name="Volume:", value=f"`{self.volume}%`")
        embed.add_field(name="Queue Length:", value=f"`{str(self.queue.qsize())}`")
        embed.add_field(name="Queue looped:", value=f"`{self.queue_loop}`")
        embed.add_field(name="Requester:", value=self.current.requester.mention)
        embed.add_field(name="Paused?", value=f"`{self.paused}`")
        return await self.current.channel.send(embed=embed)