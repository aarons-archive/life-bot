import re

import spotify
from discord.ext import commands

import granitepy
from cogs.utilities import checks
from cogs.voice.utilities import objects


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.granitepy = granitepy.Client(self.bot)

        self.bot.http_spotify = spotify.HTTPClient(client_id=self.bot.config.SPOTIFY_API_ID, client_secret=self.bot.config.SPOTIFY_API_SECRET)
        self.bot.spotify = spotify.Client(client_id=self.bot.config.SPOTIFY_API_ID, client_secret=self.bot.config.SPOTIFY_API_SECRET)

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
    @checks.is_member_connected()
    async def join(self, ctx):
        """
        Join or move to the users voice channel.
        """

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
    @checks.is_member_connected()
    async def play(self, ctx, *, search: str):
        """
        Play a track using a link or search query.

        `search`: The name/link of the track you want to play.
        """

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        async with ctx.channel.typing():

            spotify_regex = re.compile("https://open.spotify.com?.+(album|playlist|track)/([a-zA-Z0-9]+)").match(search)
            if spotify_regex:

                url_type, url_id = spotify_regex.groups()

                if url_type == "track":
                    tracks = await self.bot.spotify.get_track(url_id)
                elif url_type == "album":
                    result = await self.bot.spotify.get_album(url_id)
                    tracks = await result.get_all_tracks()
                elif url_type == "playlist":
                    result = spotify.Playlist(self.bot.spotify, await self.bot.http_spotify.get_playlist(url_id))
                    tracks = await result.get_all_tracks()
                if not tracks:
                    return await ctx.send(f"That spotify link was not recognised.")

                if isinstance(tracks, spotify.Track):
                    track = objects.SpotifyTrack(ctx=ctx, title=f"{tracks.name} - {tracks.artist.name}", uri=tracks.url, length=tracks.duration)
                    ctx.player.queue.put(track)
                    return await ctx.send(f"Added the spotify track **{track.title}** to the queue.")
                else:
                    tracks = [objects.SpotifyTrack(ctx=ctx, title=f"{track.name} - {track.artist.name}", uri=track.url, length=track.duration) for track in tracks]
                    ctx.player.queue.extend(tracks)
                    return await ctx.send(f"Added the spotify album/playlist **{result.name}** to the queue with a total of **{len(tracks)}** entries.")
            else:

                result = await ctx.player.get_result(ctx=ctx, query=search)
                if not result:
                    return await ctx.send(f"There were no tracks found for the youtube search `{search}`.")

                if isinstance(result, granitepy.Playlist):
                    ctx.player.queue.extend(result)
                    return await ctx.send(f"Added the playlist **{result.name}** to the queue with a total of **{len(result.tracks)}** entries.")
                if isinstance(result, granitepy.Track):
                    if result.is_stream:
                        return await ctx.send("The requested track is a live stream.")
                    ctx.player.queue.put(result)
                    return await ctx.send(f"Added the track **{result.title}** to the queue.")

    @commands.command(name="leave", aliases=["disconnect", "stop"])
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def leave(self, ctx):
        """
        Leave the current voice channel.
        """

        ctx.player.queue.clear()
        ctx.player.player_loop.cancel()
        await ctx.player.destroy()

        return await ctx.send(f"Left the voice channel `{ctx.guild.me.voice.channel}`.")

    @commands.command(name="skip")
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def skip(self, ctx, amount: int = 1):
        """
        Skip to the next track in the queue.

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
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def pause(self, ctx):
        """
        Pause the player.
        """

        if ctx.player.is_paused:
            return await ctx.send("The player is already paused.")

        await ctx.player.set_pause(True)
        return await ctx.send(f"Paused the player.")

    @commands.command(name="resume")
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def resume(self, ctx):
        """
        Resume the player.
        """

        if not ctx.player.is_paused:
            return await ctx.send("The player is not paused.")

        await ctx.player.set_pause(False)
        return await ctx.send(f"Resumed the player.")

    @commands.command(name="volume", aliases=["vol"])
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def volume(self, ctx, volume: int = None):
        """
        Change the volume of the player.

        `volume`: The percentage to change the volume too, can be between 0 and 100.
        """

        if not volume and not volume == 0:
            return await ctx.send(f"The current volume is `{ctx.player.volume}%`.")

        if volume < 0 or volume > 100:
            return await ctx.send(f"Please enter a value between `1` and and `100`.")

        await ctx.player.set_volume(volume)
        return await ctx.send(f"Changed the players volume to `{ctx.player.volume}%`.")

    @commands.command(name="seek")
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def seek(self, ctx, seconds: int = None):
        """
        Change the position of the player.

        `position`: The position of the track to skip to in seconds.
        """

        if not ctx.player.current.is_seekable:
            return await ctx.send("This track is not seekable.")

        if not seconds and not seconds == 0:
            return await ctx.send(f"The current position is {self.bot.utils.format_time(ctx.player.position / 1000)}")

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.player.current.length:
            return await ctx.send(f"Please enter a value between `1` and `{round(ctx.player.current.length / 1000)}`.")

        await ctx.player.seek(milliseconds)
        return await ctx.send(f"Changed the players position to `{self.bot.utils.format_time(milliseconds / 1000)}`.")

    @commands.command(name="now_playing", aliases=["np"])
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def now_playing(self, ctx):
        """
        Display information about the current track.
        """

        return await ctx.player.invoke_controller()

    @commands.command(name="queue")
    @checks.is_player_connected()
    async def queue(self, ctx):
        """
        Display the queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        title = "\n"
        if ctx.player.current:
            title = f"__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | " \
                    f"`{self.bot.utils.format_time(round(ctx.player.current.length) / 1000)}` | " \
                    f"`Requested by:` {ctx.player.current.requester.mention}\n\n" \
                    f"__**Up next:**__: Showing `{min([10, ctx.player.queue.size])}` out of `{ctx.player.queue.size}` entries in the queue.\n"

        entries = []
        for index, track in enumerate(ctx.player.queue.queue_list):
            entries.append(f"**{index + 1}.** [{str(track.title)}]({track.uri}) | "
                           f"`{self.bot.utils.format_time(round(track.length) / 1000)}` | "
                           f"`Requested by:` {track.requester.mention}\n")

        time = sum(track.length for track in ctx.player.queue.queue_list)

        footer = f"\nThere are `{ctx.player.queue.size}` track(s) in the queue with a total time of `{self.bot.utils.format_time(round(time) / 1000)}`"

        return await ctx.paginate_embed(header=title, footer=footer, entries=entries, entries_per_page=10)

    @commands.command(name="shuffle")
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def shuffle(self, ctx):
        """
        Shuffle the queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        ctx.player.queue.shuffle()
        return await ctx.send(f"The queue has been shuffled.")

    @commands.command(name="clear")
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def clear(self, ctx):
        """
        Clear the queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        ctx.player.queue.clear()
        return await ctx.send(f"Cleared the queue.")

    @commands.command(name="reverse")
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def reverse(self, ctx):
        """
        Reverse the queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        ctx.player.queue.reverse()
        return await ctx.send(f"Reversed the queue.")

    @commands.command(name="loop")
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def loop(self, ctx):
        """
        Loop the queue.
        """

        if ctx.player.queue_loop is True:
            ctx.player.queue_loop = False
            return await ctx.send(f"The queue will stop looping.")

        ctx.player.queue_loop = True
        return await ctx.send(f"The queue will now loop.")

    @commands.command(name="remove")
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def remove(self, ctx, entry: int = 0):
        """
        Remove an entry from the queue.

        `entry`: The position of the entry you want to remove.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send("The queue is empty.")

        if entry <= 0 or entry > ctx.player.queue.size:
            return await ctx.send(f"That was not a valid track entry number.")

        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f"Removed `{item.title}` from the queue.")

    @commands.command(name="move")
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def move(self, ctx, entry_1: int = 0, entry_2: int = 0):
        """
        Move an entry from one position to another in the queue.

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

        ctx.player.queue.put_pos(item, entry_2 - 1)
        return await ctx.send(f"Moved `{item.title}` from position `{entry_1}` to position `{entry_2}`.")


def setup(bot):
    music = Music(bot)

    bot.add_cog(music)
    bot.loop.create_task(music.initiate_nodes())


def teardown(bot):
    del bot.granitepy
