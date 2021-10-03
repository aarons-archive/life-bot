# Future
from __future__ import annotations

# Standard Library
import math
from typing import Literal

# Packages
import discord
import humanize
import slate
from discord.ext import commands
from slate import obsidian

# My stuff
from core import colours, config, emojis
from core.bot import Life
from utilities import checks, context, converters, custom, enums, exceptions, utils


class Options(commands.FlagConverter, delimiter=" ", prefix="--", case_insensitive=True):
    music: bool = False
    soundcloud: bool = False
    local: bool = False
    http: bool = False
    next: bool = False
    now: bool = False


class QueueOptions(commands.FlagConverter, delimiter=" ", prefix="--", case_insensitive=True):
    next: bool = False
    now: bool = False


class SearchOptions(commands.FlagConverter, delimiter=" ", prefix="--", case_insensitive=True):
    music: bool = False
    soundcloud: bool = False
    local: bool = False
    http: bool = False


def get_source(flags: Options | SearchOptions) -> slate.Source:

    if flags.music:
        return slate.Source.YOUTUBE_MUSIC
    elif flags.soundcloud:
        return slate.Source.SOUNDCLOUD
    elif flags.local:
        return slate.Source.LOCAL
    elif flags.http:
        return slate.Source.HTTP

    return slate.Source.YOUTUBE


def setup(bot: Life) -> None:
    bot.add_cog(Voice(bot=bot))


class Voice(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    #

    async def load(self) -> None:

        for node in config.NODES:
            try:
                await self.bot.slate.create_node(
                    bot=self.bot,
                    identifier=node["identifier"],
                    host=node["host"],
                    port=node["port"],
                    password=node["password"],
                    spotify_client_id=config.SPOTIFY_CLIENT_ID,
                    spotify_client_secret=config.SPOTIFY_CLIENT_SECRET,
                )
            except slate.NodeConnectionError:
                continue

    # Events

    @commands.Cog.listener()
    async def on_obsidian_track_start(self, player: custom.Player, _: obsidian.TrackStart) -> None:
        await player.handle_track_start()

    @commands.Cog.listener()
    async def on_obsidian_track_end(self, player: custom.Player, _: obsidian.TrackEnd) -> None:
        await player.handle_track_over()

    @commands.Cog.listener()
    async def on_obsidian_track_exception(self, player: custom.Player, _: obsidian.TrackException) -> None:
        await player.handle_track_error()

    @commands.Cog.listener()
    async def on_obsidian_track_stuck(self, player: custom.Player, _: obsidian.TrackStuck) -> None:
        await player.handle_track_error()

    # Join/Leave commands

    @commands.command(name="join", aliases=["summon", "connect"])
    @checks.is_author_connected(same_channel=False)
    async def join(self, ctx: context.Context) -> None:
        """
        Joins the bot to your voice channel.
        """

        if ctx.voice_client and ctx.voice_client.is_connected() is True:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"I am already connected to {ctx.voice_client.voice_channel.mention}.",
            )

        # noinspection PyTypeChecker
        await ctx.author.voice.channel.connect(cls=custom.Player)
        ctx.voice_client._text_channel = ctx.channel

        await ctx.send(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Joined {ctx.voice_client.voice_channel.mention}."))

    @commands.command(name="disconnect", aliases=["dc", "leave", "destroy"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def disconnect(self, ctx: context.Context) -> None:
        """
        Disconnects the bot its voice channel.
        """

        await ctx.send(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Left {ctx.voice_client.voice_channel.mention}."))
        await ctx.voice_client.disconnect()

    # Play commands

    @commands.command(name="play", aliases=["p"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play(self, ctx: context.Context, query: str, *, options: Options) -> None:
        """
        Queues tracks with the given name or url.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [YouTube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-play If I Can't Have You by Shawn Mendes --now`
        `l-play Señorita by Shawn Mendes --next`
        `l-play Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=get_source(options))

    @commands.command(name="search")
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def search(self, ctx: context.Context, query: str, *, options: Options) -> None:
        """
        Choose which track to play based on a search.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [YouTube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-search If I Can't Have You by Shawn Mendes --now`
        `l-search Señorita by Shawn Mendes --next`
        `l-search Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=get_source(options), choose=True)

    # Platform specific play commands

    @commands.command(name="youtubemusic", aliases=["youtube-music", "youtube_music", "ytmusic", "yt-music", "yt_music", "ytm"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def youtube_music(self, ctx: context.Context, query: str, *, options: QueueOptions) -> None:
        """
        Queues tracks from YouTube music with the given name or url.

        **query**: The query to search for tracks with.

        **Flags:**
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-youtube-music Lost In Japan by Shawn Mendes --now`
        `l-ytm If I Can't Have You by Shawn Mendes --next`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.YOUTUBE_MUSIC)

    @commands.command(name="soundcloud", aliases=["sc"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def soundcloud(self, ctx: context.Context, query: str, *, options: QueueOptions) -> None:
        """
        Queues tracks from soundcloud with the given name or url.

        **query**: The query to search for tracks with.

        **Flags:**
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-soundcloud Lost In Japan by Shawn Mendes --now`
        `l-sc If I Can't Have You by Shawn Mendes --next`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.SOUNDCLOUD)

    # Queue specific play commands

    @commands.command(name="playnext", aliases=["play-next", "play_next", "pnext"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play_next(self, ctx: context.Context, query: str, *, options: SearchOptions) -> None:
        """
        Queues tracks at the start of the queue.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [YouTube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.

        **Usage:**
        `l-play-next Lost In Japan by Shawn Mendes --music`
        `l-pnext If I Can't Have You by Shawn Mendes --soundcloud`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, next=True, source=get_source(options))

    @commands.command(name="playnow", aliases=["play-now", "play_now", "pnow"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play_now(self, ctx: context.Context, query: str, *, options: SearchOptions) -> None:
        """
        Queues tracks and skips the current track.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [YouTube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.

        **Usage:**
        `l-play-now Lost In Japan by Shawn Mendes --music`
        `l-pnow If I Can't Have You by Shawn Mendes --soundcloud`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=True, source=get_source(options))

    # Pause/Resume commands

    @commands.command(name="pause", aliases=["stop"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def pause(self, ctx: context.Context) -> None:
        """
        Pauses the current track.
        """

        if ctx.voice_client.paused is True:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The player is already paused."
            )

        await ctx.voice_client.set_pause(True)
        await ctx.reply(embed=utils.embed(emoji=emojis.PAUSED, description="The player is now **paused**."))

    @commands.command(name="resume", aliases=["continue", "unpause"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def resume(self, ctx: context.Context) -> None:
        """
        Resumes the current track.
        """

        if ctx.voice_client.paused is False:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The player is not paused."
            )

        await ctx.voice_client.set_pause(False)
        await ctx.reply(embed=utils.embed(emoji=emojis.PLAYING, description="The player is now **resumed**."))

    # Seek commands

    @commands.command(name="seek")
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def seek(self, ctx: context.Context, *, time: converters.TimeConverter) -> None:
        """
        Seeks to a position in the current track.

        **time**: The position to seek too.
        """

        # noinspection PyTypeChecker
        milliseconds = time * 1000

        if 0 < milliseconds > ctx.voice_client.current.length:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That is not a valid amount of time, please choose a time between **0s** and "
                            f"**{utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(milliseconds)

        await ctx.reply(
            embed=utils.embed(
                emoji=emojis.SEEK_FORWARD,
                description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**.",
            )
        )

    @commands.command(name="forward", aliases=["fwd"])
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def forward(self, ctx: context.Context, *, time: converters.TimeConverter) -> None:
        """
        Seeks forward on the current track.

        **time**: The amount of time to seek forward.
        """

        # noinspection PyTypeChecker
        milliseconds = time * 1000

        position = ctx.voice_client.position
        remaining = ctx.voice_client.current.length - position

        if milliseconds >= remaining:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That is not a valid amount of time. "
                            f"Please choose an amount lower than **{utils.format_seconds(remaining // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(position + milliseconds)

        await ctx.reply(
            embed=utils.embed(
                emoji=emojis.SEEK_FORWARD,
                description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**.",
            )
        )

    @commands.command(name="rewind", aliases=["rwd", "backward", "bckwd"])
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def rewind(self, ctx: context.Context, *, time: converters.TimeConverter) -> None:
        """
        Seeks backward on the current track.

        **time**: The amount of time to seek backward.
        """

        # noinspection PyTypeChecker
        milliseconds = time * 1000

        position = ctx.voice_client.position

        if milliseconds >= ctx.voice_client.position:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That is not a valid amount of time. "
                            f"Please choose an amount lower than **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(position - milliseconds)

        await ctx.reply(
            embed=utils.embed(
                emoji=emojis.SEEK_BACK,
                description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**.",
            )
        )

    @commands.command(name="replay")
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def replay(self, ctx: context.Context) -> None:
        """
        Seeks to the start of the current track.
        """

        await ctx.voice_client.set_position(0)

        await ctx.reply(
            embed=utils.embed(
                emoji=emojis.REPEAT,
                description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**.",
            )
        )

    # Loop commands

    @commands.command(name="loop", aliases=["loop-current", "loop_current", "repeat"])
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def loop(self, ctx: context.Context) -> None:
        """
        Loops the current track.
        """

        if ctx.voice_client.queue.loop_mode is not slate.QueueLoopMode.CURRENT:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        await ctx.reply(
            embed=utils.embed(
                emoji=emojis.LOOP_CURRENT,
                description=f"The queue looping mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
            )
        )

    @commands.command(name="queueloop", aliases=["loopqueue", "loop-queue", "loop_queue", "qloop"])
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def queueloop(self, ctx: context.Context) -> None:
        """
        Loops the queue.
        """

        if ctx.voice_client.queue.loop_mode is not slate.QueueLoopMode.QUEUE:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.QUEUE)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        await ctx.reply(
            embed=utils.embed(
                emoji=emojis.LOOP,
                description=f"The queue looping mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
            )
        )

    # Skip commands

    @commands.command(
        name="skip",
        aliases=[
            "s",
            "voteskip",
            "vote-skip",
            "vote_skip",
            "vs",
            "forceskip",
            "force-skip",
            "force_skip",
            "fs",
            "next",
        ],
    )
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def skip(self, ctx: context.Context, amount: int = 1) -> None:
        """
        Votes to skip the current track.
        """

        try:
            await commands.check_any(  # type: ignore
                checks.is_owner(),
                checks.is_guild_owner(),
                checks.is_track_requester(),
                checks.has_any_permissions(manage_guild=True, kick_members=True, ban_members=True, manage_messages=True, manage_channels=True),
            ).predicate(ctx=ctx)

        except commands.CheckAnyFailure:

            if ctx.author not in ctx.voice_client.listeners:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You can not vote to skip as you are currently deafened.",
                )

            if ctx.author.id in ctx.voice_client.skip_request_ids:
                ctx.voice_client.skip_request_ids.remove(ctx.author.id)
                message = "Removed your vote to skip, "
            else:
                ctx.voice_client.skip_request_ids.add(ctx.author.id)
                message = "Added your vote to skip, "

            skips_needed = math.floor(75 * len(ctx.voice_client.listeners) / 100)

            if len(ctx.voice_client.skip_request_ids) < skips_needed:
                raise exceptions.EmbedError(
                    colour=colours.GREEN,
                    emoji=emojis.TICK,
                    description=f"{message} currently on **{len(ctx.voice_client.skip_request_ids)}** out of **{skips_needed}** votes needed to skip.",
                )

            await ctx.voice_client.stop()

            await ctx.reply(embed=utils.embed(emoji=emojis.NEXT, description="Skipped the current track."))
            return

        if 0 <= amount > len(ctx.voice_client.queue) + 1:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are not enough tracks in the queue to skip that many. Choose a number between **1** and **{len(ctx.voice_client.queue) + 1}**.",
            )

        for track in ctx.voice_client.queue[: amount - 1]:
            try:
                if track.requester.id != ctx.author.id:
                    raise commands.CheckAnyFailure(checks=[], errors=[])
                await commands.check_any(  # type: ignore
                    checks.is_owner(),
                    checks.is_guild_owner(),
                    checks.has_any_permissions(manage_guild=True, kick_members=True, ban_members=True, manage_messages=True, manage_channels=True),
                ).predicate(ctx=ctx)
            except commands.CheckAnyFailure:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"You do not have permission to skip the next **{amount}** tracks in the queue.",
                )

        for _ in enumerate(ctx.voice_client.queue[: amount - 1]):
            ctx.voice_client.queue.get()

        await ctx.voice_client.stop()
        await ctx.reply(embed=utils.embed(emoji=emojis.NEXT, description=f"Skipped **{amount}** track{'s' if amount != 1 else ''}."))

    # Misc

    @commands.command(name="nowplaying", aliases=["np"])
    @checks.is_voice_client_playing()
    @checks.has_voice_client(try_join=False)
    async def nowplaying(self, ctx: context.Context) -> None:
        """
        Shows the player controller.
        """

        await ctx.voice_client.controller.invoke(ctx.channel)

    @commands.command(name="save", aliases=["grab", "yoink"])
    @checks.is_voice_client_playing()
    @checks.has_voice_client(try_join=False)
    async def save(self, ctx: context.Context) -> None:
        """
        Saves the current track to your DM's.
        """

        try:
            embed = discord.Embed(
                colour=colours.MAIN,
                title=ctx.voice_client.current.title,
                url=ctx.voice_client.current.uri,
                description=f"**Author:** {ctx.voice_client.current.author}\n"
                f"**Source:** {ctx.voice_client.current.source.value.title()}\n"
                f"**Length:** {utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}\n"
                f"**Live:** {ctx.voice_client.current.is_stream()}\n"
                f"**Seekable:** {ctx.voice_client.current.is_seekable()}",
            )
            embed.set_image(
                url=ctx.voice_client.current.thumbnail
            )
            await ctx.author.send(embed=embed)
            await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description="Saved the current track to our DM's."))

        except discord.Forbidden:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="I am unable to DM you."
            )

    # Queue commands

    @commands.group(name="queue", aliases=["q"], invoke_without_command=True)
    @checks.queue_not_empty()
    @checks.has_voice_client(try_join=False)
    async def queue(self, ctx: context.Context) -> None:
        """
        Displays the queue.
        """

        entries = [
            f"**{index + 1}.** [{str(track.title)}]({track.uri}) | {utils.format_seconds(track.length // 1000)} | {track.requester.mention}"
            for index, track in enumerate(ctx.voice_client.queue)
        ]

        await ctx.paginate_embed(
            entries=entries,
            per_page=10,
            title="Queue:",
            header=f"**Total tracks:** {len(ctx.voice_client.queue)}\n"
            f"**Total time:** {utils.format_seconds(sum(track.length for track in ctx.voice_client.queue) // 1000, friendly=True)}\n\n",
        )

    @queue.command(name="detailed", aliases=["d"])
    @checks.queue_not_empty()
    @checks.has_voice_client(try_join=False)
    async def queue_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queue.
        """

        entries = []

        for index, track in enumerate(ctx.voice_client.queue):

            embed = discord.Embed(
                colour=colours.MAIN,
                description=f"Showing detailed information about track **{index + 1}** out of **{len(ctx.voice_client.queue)}** in the queue.\n\n"
                            f"[{track.title}]({track.uri})\n\n"
                            f"**Author:** {track.author}\n"
                            f"**Source:** {track.source.name.title()}\n"
                            f"**Length:** {utils.format_seconds(round(track.length) // 1000, friendly=True)}\n"
                            f"**Live:** {track.is_stream()}\n"
                            f"**Seekable:** {track.is_seekable()}\n"
                            f"**Requester:** {track.requester.mention}",
            ).set_image(
                url=track.thumbnail
            )
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue.group(name="history", invoke_without_command=True)
    @checks.has_voice_client(try_join=False)
    async def queue_history(self, ctx: context.Context) -> None:
        """
        Displays the queue history.
        """

        if not (history := list(ctx.voice_client.queue.history)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The queue history is empty."
            )

        entries = [
            f"**{index + 1}.** [{str(track.title)}]({track.uri}) | {utils.format_seconds(track.length // 1000)} | {track.requester.mention}"
            for index, track in enumerate(history)
        ]

        await ctx.paginate_embed(
            entries=entries,
            per_page=10,
            title="Queue:",
            header=f"**Total tracks:** {len(history)}\n"
                   f"**Total time:** {utils.format_seconds(sum(track.length for track in history) // 1000, friendly=True)}\n\n",
        )

    @queue_history.command(name="detailed", aliases=["d"])
    @checks.has_voice_client(try_join=False)
    async def queue_history_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queue history.
        """

        if not (history := list(ctx.voice_client.queue.history)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The queue history is empty."
            )

        entries = []

        for index, track in enumerate(history):

            embed = discord.Embed(
                colour=colours.MAIN,
                description=f"Showing detailed information about track **{index + 1}** out of **{len(history)}** in the queue history.\n\n"
                            f"[{track.title}]({track.uri})\n\n"
                            f"**Author:** {track.author}\n"
                            f"**Source:** {track.source.name.title()}\n"
                            f"**Length:** {utils.format_seconds(round(track.length) // 1000, friendly=True)}\n"
                            f"**Live:** {track.is_stream()}\n"
                            f"**Seekable:** {track.is_seekable()}\n"
                            f"**Requester:** {track.requester.mention}",
            ).set_image(
                url=track.thumbnail
            )
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    # Queue control commands

    @commands.command(name="clear")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def clear(self, ctx: context.Context) -> None:
        """
        Clears the queue.
        """

        ctx.voice_client.queue.clear()
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description="The queue has been cleared."))

    @commands.command(name="shuffle")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def shuffle(self, ctx: context.Context) -> None:
        """
        Shuffles the queue.
        """

        ctx.voice_client.queue.shuffle()
        await ctx.reply(embed=utils.embed(emoji=emojis.SHUFFLE, description="The queue has been shuffled."))

    @commands.command(name="reverse")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def reverse(self, ctx: context.Context) -> None:
        """
        Reverses the queue.
        """

        ctx.voice_client.queue.reverse()
        await ctx.reply(embed=utils.embed(emoji=emojis.DOUBLE_LEFT, description="The queue has been reversed."))

    @commands.command(name="sort")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def sort(self, ctx: context.Context, method: Literal["title", "length", "author"], reverse: bool = False) -> None:
        """
        Sorts the queue.

        **method**: The method to sort the queue with. Can be **title**, **length** or **author**.
        **reverse**: Whether to reverse the sort, as in **5, 3, 2, 4, 1** -> **5, 4, 3, 2, 1** instead of **5, 3, 2, 4, 1** -> **1, 2, 3, 4, 5**. Defaults to False.

        **Usage:**
        `l-sort title True`
        `l-sort author`
        `l-sort length True`
        """

        if method == "title":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.title, reverse=reverse)
        elif method == "author":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.author, reverse=reverse)
        elif method == "length":
            ctx.voice_client.queue._queue.sort(key=lambda track: track.length, reverse=reverse)

        await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"The queue has been sorted with method **{method}**."))

    @commands.command(name="remove")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def remove(self, ctx: context.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        **entry**: The position of the track you want to remove.
        """

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That was not a valid track entry. Choose a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        item = ctx.voice_client.queue.get(entry - 1, put_history=False)

        await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Removed **[{item.title}]({item.uri})** from the queue."))

    @commands.command(name="move")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def move(self, ctx: context.Context, entry_1: int = 0, entry_2: int = 0) -> None:
        """
        Move a track in the queue to a different position.

        **entry_1**: The position of the track you want to move from.
        **entry_2**: The position of the track you want to move too.
        """

        if entry_1 <= 0 or entry_1 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That was not a valid track entry to move from. Choose a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        if entry_2 <= 0 or entry_2 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That was not a valid track entry to move too. Choose a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        track = ctx.voice_client.queue.get(entry_1 - 1, put_history=False)
        ctx.voice_client.queue.put(track, position=entry_2 - 1)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Moved **[{track.title}]({track.uri})** from position **{entry_1}** to position **{entry_2}**.",
            )
        )

    # Effect commands

    @commands.command(name="8d")
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def _8d(self, ctx: context.Context) -> None:
        """
        Sets an 8D audio filter on the player.
        """

        if enums.Filters.ROTATION in ctx.voice_client.enabled_filters:
            await ctx.voice_client.set_filter(
                obsidian.Filter(ctx.voice_client.filter, rotation=obsidian.Rotation())
            )
            ctx.voice_client.enabled_filters.remove(enums.Filters.ROTATION)
            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**8D** audio effect is now **inactive**."
            )

        else:
            await ctx.voice_client.set_filter(
                obsidian.Filter(ctx.voice_client.filter, rotation=obsidian.Rotation(rotation_hertz=0.5))
            )
            ctx.voice_client.enabled_filters.add(enums.Filters.ROTATION)
            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**8D** audio effect is now **active**."
            )

        await ctx.reply(embed=embed)

    @commands.command(name="nightcore")
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def nightcore(self, ctx: context.Context) -> None:
        """
        Sets a nightcore audio filter on the player.
        """

        if enums.Filters.NIGHTCORE in ctx.voice_client.enabled_filters:
            await ctx.voice_client.set_filter(
                obsidian.Filter(ctx.voice_client.filter, timescale=obsidian.Timescale())
            )
            ctx.voice_client.enabled_filters.remove(enums.Filters.NIGHTCORE)
            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**Nightcore** audio effect is now **inactive**."
            )

        else:
            await ctx.voice_client.set_filter(
                obsidian.Filter(ctx.voice_client.filter, timescale=obsidian.Timescale(speed=1.12, pitch=1.12))
            )
            ctx.voice_client.enabled_filters.add(enums.Filters.NIGHTCORE)
            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**Nightcore** audio effect is now **active**."
            )

        await ctx.reply(embed=embed)

    #

    @commands.command(name="nodestats", aliases=["node-stats", "node_stats"])
    async def nodestats(self, ctx: context.Context) -> None:

        embeds = []

        for node in self.bot.slate.nodes.values():

            embed = discord.Embed(
                colour=colours.MAIN,
                title=f"Stats: {node._identifier}",
                description=f"**Players:** {len(node.players.values())}\n" \
                            f"**Active players:** {len([player for player in node.players.values() if player.is_playing()])}\n\n"
            )

            if node._stats:
                embed.description += f"**Threads (running):** {node._stats.threads_running}\n" \
                                     f"**Threads (daemon):** {node._stats.threads_daemon}\n" \
                                     f"**Threads (peak):** {node._stats.threads_peak}\n\n" \
                                     f"**Memory (init):** {humanize.naturalsize(node._stats.heap_used_init + node._stats.non_heap_used_init)}\n" \
                                     f"**Memory (max):** {humanize.naturalsize(node._stats.heap_used_max + node._stats.non_heap_used_max)}\n" \
                                     f"**Memory (committed):** " \
                                     f"{humanize.naturalsize(node._stats.heap_used_committed + node._stats.non_heap_used_committed)}\n" \
                                     f"**Memory (used):** {humanize.naturalsize(node._stats.heap_used_used + node._stats.non_heap_used_used)}\n\n" \
                                     f"**CPU (cores):** {node._stats.cpu_cores}\n"

            embeds.append(embed)

        await ctx.paginate_embeds(entries=embeds)

    # Debug commands

    @commands.is_owner()
    @commands.command(name="voiceclients", aliases=["voice-clients", "voice_clients", "vcs"])
    async def voiceclients(self, ctx: context.Context) -> None:

        entries = []

        for node in self.bot.slate.nodes.values():
            for player in node.players.values():

                current = f"[{player.current.title}]({player.current.uri})" if player.current else "None"
                position = \
                    f"{utils.format_seconds(player.position // 1000)} / {utils.format_seconds(player.current.length // 1000)}" \
                    if player.current \
                    else "N/A"

                entry = f"**• {player.channel.guild.id}**\n" \
                        f"**Guild:** {player.channel.guild}\n" \
                        f"**Voice channel:** {player.voice_channel} `{getattr(player.voice_channel, 'id', None)}`\n" \
                        f"**Text channel:** {player.text_channel} `{getattr(player.text_channel, 'id', None)}`\n" \
                        f"**Current track:** {current}\n" \
                        f"**Position:** {position}\n" \
                        f"**Paused:** {player.paused}\n" \
                        f"**Listeners:** {len(player.listeners)}\n" \

                entries.append(entry)

        await ctx.paginate_embed(entries=entries, per_page=3)

    @commands.is_owner()
    @commands.command(name="voiceclient", aliases=["voice-client", "voice_client", "vc"])
    async def voiceclient(self, ctx: context.Context, server: discord.Guild = utils.MISSING) -> None:

        guild = server or ctx.guild

        if not (player := self.bot.slate.players.get(guild.id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="That guild does not have a voice client."
            )

        current = f"[{player.current.title}]({player.current.uri})" if player.current else "n/a"
        requester = f"{player.current.requester} `{player.current.requester.id}`" if player.current else 'n/a'
        position = f"{utils.format_seconds(player.position // 1000)} / {utils.format_seconds(player.current.length // 1000)}" if player.current else "n/a"

        embed = discord.Embed(
            colour=colours.MAIN,
            title=f"{guild.name}",
        )
        embed.add_field(
            name="__Player info:__",
            value=f"**Voice channel:** {player.voice_channel} `{getattr(player.voice_channel, 'id', 'n/a')}`\n"
                  f"**Text channel:** {player.text_channel} `{getattr(player.text_channel, 'id', 'n/a')}`\n"
                  f"**Is playing:** {player.is_playing()}\n"
                  f"**Is paused:** {player.is_paused()}\n"
                  f"**Filter:** {player.filter}",
            inline=False
        )
        embed.add_field(
            name=f"__Queue info:__",
            value=f"**Loop mode:** {player.queue.loop_mode.name.title()}\n"
                  f"**Length:** {len(player.queue)}\n"
                  f"**Total time:** {utils.format_seconds(sum(track.length for track in player.queue) // 1000, friendly=True)}\n",
            inline=False
        )
        embed.add_field(
            name="__Track info:__",
            value=f"**Current track:** {current}\n"
                  f"**Author:** {getattr(player.current, 'author', 'n/a')}\n"
                  f"**Position:** {position}\n"
                  f"**Is Stream:** {player.current.is_stream() if player.current else 'n/a'}\n"
                  f"**Is Seekable:** {player.current.is_seekable() if player.current else 'n/a'}\n"
                  f"**Source:** {player.current.source.value.title() if player.current else 'n/a'}\n"
                  f"**Requester:** {requester}\n",
            inline=False
        )
        embed.set_footer(
            text=f"ID: {guild.id}"
        )
        embed.set_thumbnail(
            url=utils.icon(guild)
        )

        await ctx.send(embed=embed)
