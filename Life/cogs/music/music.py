import granitepy
from discord.ext import commands

from cogs.music import objects
from utilities import utils


def is_player_connected():
    async def predicate(ctx):
        if not ctx.player.is_connected:
            raise commands.CheckFailure(f"I am not connected to any voice channels.")
        return True
    return commands.check(predicate)


def is_player_playing():
    async def predicate(ctx):
        if not ctx.player.is_playing:
            raise commands.CheckFailure(f"I am not currently playing anything.")
        return True
    return commands.check(predicate)


def is_member_connected():
    async def predicate(ctx):
        if not ctx.author.voice:
            raise commands.CheckFailure(f"You are not connected to any voice channels.")
        return True
    return commands.check(predicate)


def is_member_in_channel():
    async def predicate(ctx):
        if not ctx.player.voice_channel.id == ctx.author.voice.channel.id:
            raise commands.CheckFailure(f"You are not connected to the same voice channel as me.")
        return True
    return commands.check(predicate)


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.granitepy = granitepy.Client(self.bot)

    async def initiate_nodes(self):

        await self.bot.wait_until_ready()

        for n in self.bot.config.NODES.values():
            try:
                await self.bot.granitepy.create_node(
                    host=n["host"],
                    port=n["port"],
                    password=n["password"],
                    identifier=n["identifier"]
                )
                print(f"[GRANITEPY] Node {n['identifier']} connected.")
            except granitepy.NodeConnectionFailure as e:
                print(f"[GRANITEPY] {e}")
                continue

    @commands.command(name="join", aliases=["connect"])
    @is_member_connected()
    async def join(self, ctx):
        """Join or move to the users voice channel."""

        channel = ctx.author.voice.channel
        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(channel)
            return await ctx.send(f"Joined the voice channel `{channel}`.")

        if ctx.player.voice_channel.id != channel.id:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(channel)
            return await ctx.send(f"Moved to the voice channel `{channel}`.")

        return await ctx.send("I am already in this voice channel.")

    @commands.command(name="play")
    @is_member_connected()
    async def play(self, ctx, *, search: str):
        """Play a track using a link or search query.

        `search`: The name/link of the track you want to play.
        """

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        await ctx.trigger_typing()

        result = await ctx.player.get_tracks(search)
        if not result:
            return await ctx.send(f"No results found for the search term `{search}`.")

        if isinstance(result, granitepy.Playlist):
            playlist = objects.Playlist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)
            for track in playlist.tracks:
                await ctx.player.queue.put(track)
            return await ctx.send(f"Added the playlist **{playlist.name}** to the queue with a total of **{len(playlist.tracks)}** entries.")
        else:
            track = objects.Track(track_id=result[0].track_id, info=result[0].info, ctx=ctx)
            if track.is_stream:
                return await ctx.send("I am unable to play live streams.")
            await ctx.player.queue.put(track)
            return await ctx.send(f"Added the track **{track.title}** to the queue.")

    @commands.command(name="leave", aliases=["disconnect", "stop"])
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def leave(self, ctx):
        """Leave the current voice channel."""

        ctx.player.queue.clear()
        ctx.player.player_loop.cancel()
        await ctx.player.destroy()

        return await ctx.send(f"Left the voice channel `{ctx.guild.me.voice.channel}`.")

    @commands.command(name="skip")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    @is_player_playing()
    async def skip(self, ctx, amount: int = 1):
        """Skip to the next track in the queue.

        This will auto-skip if you are the requester of the current track, otherwise a vote will start.

        `amount`: An optional number for skipping multiple tracks at once. (You must be the requester of all the the tracks)
        """

        if ctx.player.current.requester.id != ctx.author.id:
            return await ctx.send("Do vote skipping u sad fuck.")

        if amount <= 0 or amount > ctx.player.queue.size + 1:
            return await ctx.send(f"That is not a valid amount of tracks to skip. Please choose a value between `1` and `{ctx.player.queue.size + 1}` inclusive")

        for track in ctx.player.queue.queue_list[:amount - 1]:
            if not track.requester.id == ctx.author.id:
                return await ctx.send(f"You are not the requester of all `{amount}` of the next tracks in the queue.")
            await ctx.player.queue.get_pos(0)

        await ctx.player.stop()
        return await ctx.send(f"The current tracks requester has skipped `{amount}` track(s).")

    @commands.command(name="pause")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    @is_player_playing()
    async def pause(self, ctx):
        """Pause the player."""

        if ctx.player.is_paused:
            return await ctx.send("The player is already paused.")

        await ctx.player.set_pause(True)
        return await ctx.send(f"Paused the player.")

    @commands.command(name="resume")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    @is_player_playing()
    async def resume(self, ctx):
        """Resume the player."""

        if not ctx.player.is_paused:
            return await ctx.send("The player is not paused.")

        await ctx.player.set_pause(False)
        return await ctx.send(f"Resumed the player.")

    @commands.command(name="volume", aliases=["vol"])
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def volume(self, ctx, volume: int = None):
        """Change the volume of the player.

        `volume`: The percentage to change the volume too, can be between 0 and 100.
        """

        if not volume and not volume == 0:
            return await ctx.send(f"The current volume is `{ctx.player.volume}%`.")

        if volume < 0 or volume > 100:
            return await ctx.send(f"Please enter a value between `1` and and `100`.")

        await ctx.player.set_volume(volume)
        return await ctx.send(f"Changed the players volume to `{ctx.player.volume}%`.")

    @commands.command(name="seek")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    @is_player_playing()
    async def seek(self, ctx, seconds: int = None):
        """Change the postion of the player.

        `position`: The position of the track to skip to in seconds.
        """

        if not ctx.player.current.is_seekable:
            return await ctx.send("This track is not seekable.")

        if not seconds and not seconds == 0:
            return await ctx.send(f"The current position is {utils.format_time(ctx.player.position / 1000)}")

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.player.current.length:
            return await ctx.send(f"Please enter a value between `1` and `{round(ctx.player.current.length / 1000)}`.")

        await ctx.player.seek(milliseconds)
        return await ctx.send(f"Changed the players position to `{utils.format_time(milliseconds / 1000)}`.")

    @commands.command(name="now_playing", aliases=["np"])
    @is_player_connected()
    @is_player_playing()
    async def now_playing(self, ctx):
        """Display information about the current track."""

        return await ctx.player.invoke_controller()

    @commands.command(name="queue")
    @is_player_connected()
    async def queue(self, ctx):
        """Display the queue."""

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        if ctx.player.current:
            title = f"__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | " \
                    f"`{utils.format_time(round(ctx.player.current.length) / 1000)}` | " \
                    f"`Requested by:` {ctx.player.current.requester.mention}\n\n" \
                    f"__**Up next:**__: Showing `{min([10, ctx.player.queue.size])}` out of `{ctx.player.queue.size}` entries in the queue.\n"
        else:
            title = "\n"

        entries = []
        for index, track in enumerate(ctx.player.queue.queue_list):
            entries.append(f"**{index + 1}.** [{str(track.title)}]({track.uri}) | "
                           f"`{utils.format_time(round(track.length) / 1000)}` | "
                           f"`Requested by:` {track.requester.mention}\n")

        time = sum(track.length for track in ctx.player.queue.queue_list)

        footer = f"\nThere are `{ctx.player.queue.size}` tracks in the queue with a total time of `{utils.format_time(round(time) / 1000)}`"

        return await ctx.paginate_embed(title=title, footer=footer, entries=entries, entries_per_page=10)

    @commands.command(name="shuffle")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def shuffle(self, ctx):
        """Shuffle the queue."""

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        ctx.player.queue.shuffle()
        return await ctx.send(f"The queue has been shuffled.")

    @commands.command(name="clear")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def clear(self, ctx):
        """Clear the queue."""

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        ctx.player.queue.clear()
        return await ctx.send(f"Cleared the queue.")

    @commands.command(name="reverse")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def reverse(self, ctx):
        """Reverse the queue."""

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        ctx.player.queue.reverse()
        return await ctx.send(f"Reversed the queue.")

    @commands.command(name="loop")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def loop(self, ctx):
        """Loop the queue."""

        if ctx.player.queue_loop is True:
            ctx.player.queue_loop = False
            return await ctx.send(f"The queue will stop looping.")

        ctx.player.queue_loop = True
        return await ctx.send(f"The queue will now loop.")

    @commands.command(name="remove")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def remove(self, ctx, entry: int = 0):
        """Remove an entry from the queue.

        `entry`: The position of the entry you want to remove.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        if entry <= 0 or entry > ctx.player.queue.size:
            return await ctx.send(f"That was not a valid track entry number.")

        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f"Removed `{item.title}` from the queue.")

    @commands.command(name="move")
    @is_player_connected()
    @is_member_connected()
    @is_member_in_channel()
    async def move(self, ctx, entry_1: int = 0, entry_2: int = 0):
        """Move an entry from one position to another in the queue.

        `entry_1`: The position of the entry you want to move from.
        `entry_2`: The position of the entry you want to move too.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        if entry_1 <= 0 or entry_1 > ctx.player.queue.size:
            return await ctx.send(f"That was not a valid track to move from.")

        if entry_2 <= 0 or entry_2 > ctx.player.queue.size:
            return await ctx.send(f"That was not a valid track to move too.")

        item = await ctx.player.queue.get_pos(entry_1 - 1)

        await ctx.player.queue.put_pos(item, entry_2 - 1)
        return await ctx.send(f"Moved `{item.title}` from position `{entry_1}` to position `{entry_2}`.")


def setup(bot):
    bot.add_cog(Music(bot))
    bot.loop.create_task(Music(bot).initiate_nodes())
