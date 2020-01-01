import granitepy
from discord.ext import commands

from cogs.music.track import Track
from utilities import utils


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.granitepy = granitepy.Client(self.bot)

    async def initiate_nodes(self):

        for n in self.bot.config.NODES.values():
            try:
                await self.bot.granitepy.create_node(
                    host=n["ip"],
                    port=n["port"],
                    password=n["password"],
                    rest_uri=n["rest_uri"],
                    identifier=n["identifier"]
                )
                print(f"[GRANITEPY] Node {n['identifier']} connected.")
            except granitepy.NodeInvalidCredentials:
                print(f"[GRANITEPY] Invalid credentials for node {n['identifier']}.")
                continue
            except granitepy.NodeConnectionFailure:
                print(f"[GRANITEPY] Failed to connect to node {n['identifier']}")
                continue

    @commands.command(name="join", aliases=["connect"])
    async def join(self, ctx):
        """Join or move to the users voice channel."""

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")
        channel = ctx.author.voice.channel

        if not ctx.player.is_connected or not ctx.guild.me.voice.channel:
            await ctx.player.connect(channel.id)
            ctx.player.channel = ctx.channel
            return await ctx.send(f"Joined the voice channel `{channel}`.")

        if ctx.guild.me.voice.channel.id != channel.id:
            await ctx.player.connect(channel.id)
            ctx.player.channel = ctx.channel
            return await ctx.send(f"Moved to the voice channel `{channel}`.")

        return await ctx.send("I am already in this voice channel.")

    @commands.command(name="leave", aliases=["disconnect", "stop"])
    async def leave(self, ctx):
        """Leave the current voice channel."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        ctx.player.queue.clear()
        await ctx.player.destroy()
        return await ctx.send(f"Left the voice channel `{ctx.guild.me.voice.channel}`.")

    @commands.command(name="search")
    async def search(self, ctx, *, search: str):
        """Search for all tracks with a given search query.

        `search`: The name of the track you want to search for.
        """

        await ctx.trigger_typing()

        tracks = await ctx.player.get_tracks(f"{search}")
        if not tracks:
            return await ctx.send(f"No results were found for the search term `{search}`.")

        results = []
        for index, track in enumerate(tracks):
            message = f"**{index + 1}.** [{track.title}]({track.uri})"
            results.append(message)

        title = f"Showing all results for the search term `{search}`\n\n"

        return await ctx.paginate_embed(entries=results, entries_per_page=10, title=title)

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        """Play a track using a link or search query.

        `search`: The name/link of the track you want to play.
        """

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")
        channel = ctx.author.voice.channel

        if not ctx.player.is_connected:
            await ctx.player.connect(channel.id)

        await ctx.trigger_typing()

        tracks = await ctx.player.get_tracks(f"{search}")
        if not tracks:
            return await ctx.send(f"No results were found for the search term `{search}`.")

        ctx.player.channel = ctx.channel

        if isinstance(tracks, granitepy.Playlist):
            for track in tracks.tracks:
                await ctx.player.queue.put(Track(track.track, track.data, ctx=ctx))
            return await ctx.send(f"Added the playlist **{tracks.title}** to the queue with a total of **{len(tracks.tracks)}** entries.")

        await ctx.player.queue.put(Track(track=tracks[0].track, data=tracks[0].data, ctx=ctx))
        return await ctx.send(f"Added the track **{tracks[0].title}** to the queue.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pause the player."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if not ctx.player.current:
            return await ctx.send("No tracks are currently playing.")

        if ctx.player.paused is True:
            return await ctx.send("The player is already paused.")

        await ctx.player.set_pause(True)
        return await ctx.send(f"Paused the player.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Resume the current track."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if not ctx.player.current:
            return await ctx.send("No tracks are currently playing.")

        if ctx.player.paused is False:
            return await ctx.send("The player is not paused.")

        await ctx.player.set_pause(False)
        return await ctx.send(f"Resumed the player.")

    @commands.command(name="skip")
    async def skip(self, ctx, amount: int = 0):
        """Skip to the next track in the queue.

        This will auto-skip if you are the requester of the current track, otherwise a vote will start.

        `amount`: An optional number for skipping multiple tracks at once. (You must be the requester of all the the tracks)
        """

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if not ctx.player.current:
            return await ctx.send("No tracks are currently playing.")

        if ctx.player.current.requester.id != ctx.author.id:
            return await ctx.send("Vote skipping coming soon.")

        if not amount:
            await ctx.player.stop()
            return await ctx.send(f"The tracks requester has skipped.")

        if amount <= 0 or amount > ctx.player.queue.size():
            return await ctx.send(f"That is not a valid amount of tracks to skip. Please choose a value between `1` and `{ctx.player.queue.size()}`")

        for track in ctx.player.queue.queue[:amount - 1]:
            if not ctx.author.id == track.requester.id:
                return await ctx.send(f"You are not the requester of all `{amount}` of the next tracks in the queue.")
            await ctx.player.queue.get_pos(0)

        await ctx.player.stop()
        return await ctx.send(f"The current tracks requester has skipped `{amount}` tracks.")

    @commands.command(name="now_playing", aliases=["np"])
    async def now_playing(self, ctx):
        """Display information about the current track.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.player.current:
            return await ctx.send("No tracks currently playing.")

        return await ctx.player.invoke_controller()

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, volume: int = None):
        """Change the volume of the player.

        `volume`: The percentage to change the volume to, can be between 0 and 100.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if not volume and not volume == 0:
            return await ctx.send(f"The current volume is `{ctx.player.volume}%`.")

        if volume < 0 or volume > 100:
            return await ctx.send(f"Please enter a value between `1` and and `100`.")

        await ctx.player.set_volume(volume)
        return await ctx.send(f"Changed the players volume to `{ctx.player.volume}%`.")

    @commands.command(name="seek")
    async def seek(self, ctx, seconds: int = None):
        """Change the postion of the player.

        `position`: The position of the track to skip to in seconds.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if not ctx.player.current:
            return await ctx.send("No tracks are currently playing.")

        if not ctx.player.current.is_seekable:
            return await ctx.send("This track is not seekable.")

        if not seconds and not seconds == 0:
            return await ctx.send(f"The current position is {utils.format_time(ctx.player.position / 1000)}")

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.player.current.length:
            return await ctx.send(f"Please enter a value between `1` and `{round(ctx.player.current.length / 1000)}`.")

        await ctx.player.seek(milliseconds)
        return await ctx.send(f"Changed the players position to `{utils.format_time(milliseconds / 1000)}`.")

    @commands.command(name="queue")
    async def queue(self, ctx):
        """Display the queue."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        title = f"__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | " \
                f"`{utils.format_time(round(ctx.player.current.length) / 1000)}` | " \
                f"`Requested by:` {ctx.player.current.requester.mention}\n\n" \
                f"__**Up next:**__: Showing `{min([10, ctx.player.queue.size()])}` out of `{ctx.player.queue.size()}` entries in the queue.\n"

        entries = []
        for index, track in enumerate(ctx.player.queue.queue):
            entries.append(f"**{index + 1}.** [{str(track.title)}]({track.uri}) | "
                           f"`{utils.format_time(round(track.length) / 1000)}` | "
                           f"`Requested by:` {track.requester.mention}\n")

        time = sum(track.length for track in ctx.player.queue.queue)

        footer = f"\nThere are `{ctx.player.queue.size()}` tracks in the queue with a total time of `{utils.format_time(round(time) / 1000)}`"

        return await ctx.paginate_embed(title=title, footer=footer, entries=entries, entries_per_page=10)

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        """Shuffle the queue."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        ctx.player.queue.shuffle()
        return await ctx.send(f"The queue has been shuffled.")

    @commands.command(name="clear")
    async def clear(self, ctx):
        """Clear the queue."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        ctx.player.queue.clear()
        return await ctx.send(f"Cleared the queue.")

    @commands.command(name="reverse")
    async def reverse(self, ctx):
        """Reverse the queue."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        ctx.player.queue.reverse()
        return await ctx.send(f"Reversed the queue.")

    @commands.command(name="loop")
    async def loop(self, ctx):
        """Loop the queue."""

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if ctx.player.queue_loop is True:
            ctx.player.queue_loop = False
            return await ctx.send(f"The queue will stop looping.")

        ctx.player.queue_loop = True
        return await ctx.send(f"The queue will now loop.")

    @commands.command(name="remove")
    async def remove(self, ctx, entry: int = 0):
        """Remove an entry from the queue.

        `entry`: The position of the entry you want to remove.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        if entry <= 0 or entry > ctx.player.queue.size():
            return await ctx.send(f"That was not a valid track entry number.")

        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f"Removed `{item.title}` from the queue.")

    @commands.command(name="move")
    async def move(self, ctx, entry_1: int = 0, entry_2: int = 0):
        """Move an entry from one position to another in the queue.

        `entry_1`: The position of the entry you want to move from.
        `entry_2`: The position of the entry you want to move too.
        """

        if not ctx.player.is_connected:
            return await ctx.send(f"I am not connected to any voice channels.")

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        if entry_1 <= 0 or entry_1 > ctx.player.queue.size():
            return await ctx.send(f"That was not a valid track to move from.")

        if entry_2 <= 0 or entry_2 > ctx.player.queue.size():
            return await ctx.send(f"That was not a valid track to move too.")

        item = await ctx.player.queue.get_pos(entry_1 - 1)

        await ctx.player.queue.put_pos(item, entry_2 - 1)
        return await ctx.send(f"Moved `{item.title}` from position `{entry_1}` to position `{entry_2}`.")


def setup(bot):
    bot.add_cog(Music(bot))
    bot.loop.create_task(Music(bot).initiate_nodes())
