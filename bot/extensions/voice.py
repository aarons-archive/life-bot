# Future
from __future__ import annotations

# Standard Library
import math
from typing import Literal

# Packages
import discord
import humanize
import slate
import slate.obsidian
from discord.ext import commands

# My stuff
from core import colours, config, emojis
from core.bot import Life
from utilities import checks, custom, enums, exceptions, objects, utils


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
        return slate.obsidian.Source.YOUTUBE_MUSIC
    elif flags.soundcloud:
        return slate.obsidian.Source.SOUNDCLOUD
    elif flags.local:
        return slate.obsidian.Source.LOCAL
    elif flags.http:
        return slate.obsidian.Source.HTTP

    return slate.obsidian.Source.YOUTUBE


def setup(bot: Life) -> None:
    bot.add_cog(Voice(bot=bot))


class Voice(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot: Life = bot

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
            except slate.obsidian.NodeConnectionError:
                continue

    # Events

    @commands.Cog.listener()
    async def on_obsidian_track_start(self, player: custom.Player, _: slate.obsidian.TrackStart) -> None:
        await player.handle_track_start()

    @commands.Cog.listener()
    async def on_obsidian_track_end(self, player: custom.Player, _: slate.obsidian.TrackEnd) -> None:
        await player.handle_track_over()

    @commands.Cog.listener()
    async def on_obsidian_track_exception(self, player: custom.Player, _: slate.obsidian.TrackException) -> None:
        await player.handle_track_error()

    @commands.Cog.listener()
    async def on_obsidian_track_stuck(self, player: custom.Player, _: slate.obsidian.TrackStuck) -> None:
        await player.handle_track_error()

    # Join/leave commands

    @commands.command(name="join", aliases=["summon", "connect"])
    async def join(self, ctx: custom.Context) -> None:
        """
        Joins the bot to your voice channel.
        """

        if ctx.voice_client and ctx.voice_client.is_connected():
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"I am already connected to {ctx.voice_client.voice_channel.mention}.",
            )

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="You must be connected to a voice channel to use this command.",
            )

        # noinspection PyTypeChecker
        await ctx.author.voice.channel.connect(cls=custom.Player)
        ctx.voice_client._text_channel = ctx.channel

        await ctx.send(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Joined {ctx.voice_client.voice_channel.mention}."))

    @commands.command(name="disconnect", aliases=["dc", "leave", "destroy"])
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def disconnect(self, ctx: custom.Context) -> None:
        """
        Disconnects the bot from its voice channel.
        """

        await ctx.send(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Left {ctx.voice_client.voice_channel.mention}."))
        await ctx.voice_client.disconnect()

    # Play commands

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: custom.Context, query: str, *, options: Options) -> None:
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

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            if (command := ctx.bot.get_command("join")) is None or await command.can_run(ctx) is True:
                await ctx.invoke(command)

        # noinspection PyUnresolvedReferences
        await checks.is_author_connected().predicate(ctx=ctx)

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=get_source(options))

    @commands.command(name="search")
    async def search(self, ctx: custom.Context, query: str, *, options: Options) -> None:
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

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            if (command := ctx.bot.get_command("join")) is None or await command.can_run(ctx) is True:
                await ctx.invoke(command)

        # noinspection PyUnresolvedReferences
        await checks.is_author_connected().predicate(ctx=ctx)

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=get_source(options), choose=True)

    @commands.command(name="youtube-music", aliases=["youtube_music", "youtubemusic", "yt-music", "yt_music", "ytmusic", "ytm"])
    async def youtube_music(self, ctx: custom.Context, query: str, *, options: QueueOptions) -> None:
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

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            if (command := ctx.bot.get_command("join")) is None or await command.can_run(ctx) is True:
                await ctx.invoke(command)

        # noinspection PyUnresolvedReferences
        await checks.is_author_connected().predicate(ctx=ctx)

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.YOUTUBE_MUSIC)

    @commands.command(name="soundcloud", aliases=["sc"])
    async def soundcloud(self, ctx: custom.Context, query: str, *, options: QueueOptions) -> None:
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

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            if (command := ctx.bot.get_command("join")) is None or await command.can_run(ctx) is True:
                await ctx.invoke(command)

        # noinspection PyUnresolvedReferences
        await checks.is_author_connected().predicate(ctx=ctx)

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.SOUNDCLOUD)

    @commands.command(name="play-next", aliases=["play_next", "playnext", "pnext"])
    async def play_next(self, ctx: custom.Context, query: str, *, options: SearchOptions) -> None:
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

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            if (command := ctx.bot.get_command("join")) is None or await command.can_run(ctx) is True:
                await ctx.invoke(command)

        # noinspection PyUnresolvedReferences
        await checks.is_author_connected().predicate(ctx=ctx)

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, next=True, source=get_source(options))

    @commands.command(name="play-now", aliases=["play_now", "playnow", "pnow"])
    async def play_now(self, ctx: custom.Context, query: str, *, options: SearchOptions) -> None:
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

        if ctx.voice_client is None or ctx.voice_client.is_connected() is False:
            if (command := ctx.bot.get_command("join")) is None or await command.can_run(ctx) is True:
                await ctx.invoke(command)

        # noinspection PyUnresolvedReferences
        await checks.is_author_connected().predicate(ctx=ctx)

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query, ctx=ctx, now=True, source=get_source(options))

    # Pause/resume commands

    @commands.command(name="pause", aliases=["stop"])
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def pause(self, ctx: custom.Context) -> None:
        """
        Pauses the current track.
        """

        if ctx.voice_client.paused is True:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="The played is already paused."
            )

        await ctx.voice_client.set_pause(True)
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="The player is now **paused**."))

    @commands.command(name="resume", aliases=["unpause", "continue"])
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def resume(self, ctx: custom.Context) -> None:
        """
        Resumes the current track.
        """

        if ctx.voice_client.paused is False:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="The player is not paused."
            )

        await ctx.voice_client.set_pause(False)
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="The player is now **resumed**."))

    # Seek commands

    @commands.command(name="seek", aliases=["scrub"])
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def seek(self, ctx: custom.Context, *, time: objects.Time) -> None:
        """
        Seeks to a position in the current track.

        **time**: The position to seek too.

        Valid time formats include:

        - 01:10:20 (hh:mm:ss)
        - 01:20 (mm:ss)
        - 20 (ss)
        - (h:m:s)
        - (hh:m:s)
        - (h:mm:s)
        - etc

        - 1 hour 20 minutes 30 seconds
        - 1 hour 20 minutes
        - 1 hour 30 seconds
        - 20 minutes 30 seconds
        - 20 minutes
        - 30 seconds
        - 1 hour 20 minutes and 30 seconds
        - 1h20m30s
        - 20m and 30s
        - 20s
        - etc
        """

        milliseconds = time.seconds * 1000

        if 0 < milliseconds > ctx.voice_client.current.length:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That is not a valid amount of time, please choose a time between "
                            f"**0s** and **{utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(milliseconds)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

    @commands.command(name="fast-forward", aliases=["fast_forward", "fastforward", "ff", "forward", "fwd"])
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def fast_forward(self, ctx: custom.Context, *, time: objects.Time) -> None:
        """
        Seeks the player forward.

        **time**: The amount of time to seek forward.

        Valid time formats include:

        - 01:10:20 (hh:mm:ss)
        - 01:20 (mm:ss)
        - 20 (ss)
        - (h:m:s)
        - (hh:m:s)
        - (h:mm:s)
        - etc

        - 1 hour 20 minutes 30 seconds
        - 1 hour 20 minutes
        - 1 hour 30 seconds
        - 20 minutes 30 seconds
        - 20 minutes
        - 30 seconds
        - 1 hour 20 minutes and 30 seconds
        - 1h20m30s
        - 20m and 30s
        - 20s
        - etc
        """

        milliseconds = time.seconds * 1000
        position = ctx.voice_client.position
        remaining = ctx.voice_client.current.length - position

        if milliseconds >= remaining:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That was too much time to seek forward, try seeking forward an amount less than "
                            f"**{utils.format_seconds(remaining // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(position + milliseconds)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"Seeking forward **{utils.format_seconds(time.seconds, friendly=True)}**, the players position is now "
                        f"**{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

    @commands.command(name="rewind", aliases=["rwd", "backward", "bwd"])
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def rewind(self, ctx: custom.Context, *, time: objects.Time) -> None:
        """
        Seeks the player backward.

        **time**: The amount of time to seek backward.

        Valid time formats include:

        - 01:10:20 (hh:mm:ss)
        - 01:20 (mm:ss)
        - 20 (ss)
        - (h:m:s)
        - (hh:m:s)
        - (h:mm:s)
        - etc

        - 1 hour 20 minutes 30 seconds
        - 1 hour 20 minutes
        - 1 hour 30 seconds
        - 20 minutes 30 seconds
        - 20 minutes
        - 30 seconds
        - 1 hour 20 minutes and 30 seconds
        - 1h20m30s
        - 20m and 30s
        - 20s
        - etc
        """

        milliseconds = time.seconds * 1000
        position = ctx.voice_client.position

        if milliseconds >= position:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That was too much time to seek backward, try seeking backward an amount less than "
                            f"**{utils.format_seconds(position // 1000, friendly=True)}**.",
            )

        await ctx.voice_client.set_position(position - milliseconds)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"Seeking backward **{utils.format_seconds(time.seconds, friendly=True)}**, the players position is now "
                        f"**{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

    @commands.command(name="replay", aliases=["restart"])
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def replay(self, ctx: custom.Context) -> None:
        """
        Replays the current track.
        """

        await ctx.voice_client.set_position(0)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"Replaying [{ctx.voice_client.current.title}]({ctx.voice_client.current.uri}) by **{ctx.voice_client.current.author}**."
        )
        await ctx.reply(embed=embed)

    # Loop commands

    @commands.command(name="loop-current", aliases=["loop_current", "loopcurrent", "loopc", "cloop"])
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def loop_current(self, ctx: custom.Context) -> None:
        """
        Loops the current track.
        """

        if ctx.voice_client.queue.loop_mode != slate.QueueLoopMode.CURRENT:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"The queue looping mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
        )
        await ctx.reply(embed=embed)

    @commands.command(name="loop-queue", aliases=["loop_queue", "loopqueue", "loopq", "qloop", "loop"])
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def loop_queue(self, ctx: custom.Context) -> None:
        """
        Loops the queue.
        """

        if ctx.voice_client.queue.loop_mode != slate.QueueLoopMode.QUEUE:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.QUEUE)
        else:
            ctx.voice_client.queue.set_loop_mode(slate.QueueLoopMode.OFF)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"The queue looping mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**.",
        )
        await ctx.reply(embed=embed)

    # Skip command

    @commands.command(name="skip", aliases=["s", "voteskip", "vote-skip", "vote_skip", "vs", "forceskip", "force-skip", "force_skip", "fs", "next"])
    @checks.is_voice_client_playing()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def skip(self, ctx: custom.Context, amount: int = 1) -> None:
        """
        Skips the current track.

        **amount**: The amount of tracks to skip, only works if you are the bot owner, guild owner, or have the manage guild, manage message, manage channels, kick members, or ban members permissions.
        """

        try:

            await commands.check_any(  # type: ignore
                checks.is_owner(),
                checks.is_guild_owner(),
                checks.has_any_permissions(manage_guild=True, manage_messages=True, manage_channels=True, kick_members=True, ban_members=True),
            ).predicate(ctx=ctx)

            if 0 <= amount > len(ctx.voice_client.queue) + 1:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    description=f"There are not enough tracks in the queue to skip that many, try again with an amount between "
                                f"**1** and **{len(ctx.voice_client.queue) + 1}**.",
                )

            for _ in enumerate(ctx.voice_client.queue[:amount - 1]):
                ctx.voice_client.queue.get(put_history=False)

            await ctx.voice_client.stop()
            await ctx.reply(embed=utils.embed(colour=colours.GREEN, description=f"Skipped **{amount}** track{'s' if amount != 1 else ''}."))
            return

        except commands.CheckAnyFailure:

            if ctx.author.id == ctx.voice_client.current.requester.id:
                await ctx.voice_client.stop()
                await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="Skipped the current track."))
                return

            if ctx.author not in ctx.voice_client.listeners:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    description="You can not vote to skip as you are currently deafened.",
                )

            skips_needed = math.floor(75 * len(ctx.voice_client.listeners) / 100)

            if ctx.author.id not in ctx.voice_client.skip_request_ids:

                ctx.voice_client.skip_request_ids.add(ctx.author.id)

                if len(ctx.voice_client.skip_request_ids) < skips_needed:
                    embed = utils.embed(
                        colour=colours.GREEN,
                        description=f"Added your vote to skip, currently on **{len(ctx.voice_client.skip_request_ids)}** out of **{skips_needed}** votes "
                                    f"needed to skip."
                    )
                    await ctx.reply(embed=embed)
                    return

                await ctx.voice_client.stop()
                await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="Skipped the current track."))
                return

            ctx.voice_client.skip_request_ids.remove(ctx.author.id)
            await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="Removed your vote to skip."))

    # Misc

    @commands.command(name="nowplaying", aliases=["np"])
    @checks.is_voice_client_playing()
    @checks.is_voice_client_connected()
    async def nowplaying(self, ctx: custom.Context) -> None:
        """
        Shows the current track.
        """

        await ctx.voice_client.invoke_controller(ctx.channel)

    @commands.command(name="save", aliases=["grab", "yoink"])
    @checks.is_voice_client_playing()
    @checks.is_voice_client_connected()
    async def save(self, ctx: custom.Context) -> None:
        """
        Saves the current track to our DM's.
        """

        try:

            embed = utils.embed(
                title=f"{ctx.voice_client.current.title}",
                url=f"{ctx.voice_client.current.uri}",
                image=ctx.voice_client.current.thumbnail,
                description=f"**Author:** {ctx.voice_client.current.author}\n"
                            f"**Source:** {ctx.voice_client.current.source.name.title()}\n"
                            f"**Length:** {utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}\n"
                            f"**Is stream:** {ctx.voice_client.current.is_stream()}\n"
                            f"**Is seekable:** {ctx.voice_client.current.is_seekable()}\n"
                            f"**Requester:** {ctx.voice_client.current.requester} `{ctx.voice_client.current.requester.id}`"
            )
            await ctx.author.send(embed=embed)
            await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="Saved the current track to our DM's."))

        except discord.Forbidden:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="I am unable to DM you."
            )

    # Queue commands

    @commands.group(name="queue", aliases=["q"], invoke_without_command=True)
    @checks.is_queue_not_empty()
    @checks.is_voice_client_connected()
    async def queue(self, ctx: custom.Context) -> None:
        """
        Displays tracks in the queue.
        """

        queue = ctx.voice_client.queue

        await ctx.paginate_embed(
            entries=[
                f"**{index + 1}.** [{str(track.title)}]({track.uri}) | {utils.format_seconds(track.length // 1000)} | {track.requester.mention}"
                for index, track in enumerate(queue)
            ],
            per_page=10,
            title="Queue:",
            header=f"**Tracks:** {len(queue)}\n"
                   f"**Time:** {utils.format_seconds(sum(track.length for track in queue) // 1000, friendly=True)}\n"
                   f"**Loop mode:** {queue.loop_mode.name.title()}\n\n",
        )

    @queue.command(name="detailed", aliases=["d"])
    @checks.is_queue_not_empty()
    @checks.is_voice_client_connected()
    async def queue_detailed(self, ctx: custom.Context) -> None:
        """
        Displays detailed information about the tracks in the queue.
        """

        entries = []

        for track in ctx.voice_client.queue:

            embed = utils.embed(
                title=track.title,
                url=track.uri,
                description=f"**Author:** {track.author}\n"
                            f"**Length:** {utils.format_seconds(round(track.length) // 1000, friendly=True)}\n"
                            f"**Source:** {track.source.name.title()}\n"
                            f"**Requester:** {track.requester.mention} `{track.requester.id}`\n"
                            f"**Is stream:** {track.is_stream()}\n"
                            f"**Is seekable:** {track.is_seekable()}\n",
                image=track.thumbnail
            )
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue.group(name="history", aliases=["h"], invoke_without_command=True)
    @checks.is_queue_history_not_empty()
    @checks.is_voice_client_connected()
    async def queue_history(self, ctx: custom.Context) -> None:
        """
        Displays tracks in the queue history.
        """

        history = ctx.voice_client.queue._queue_history

        await ctx.paginate_embed(
            entries=[
                f"**{index + 1}.** [{str(track.title)}]({track.uri}) | {utils.format_seconds(track.length // 1000)} | {track.requester.mention}"
                for index, track in enumerate(history)
            ],
            per_page=10,
            title="Queue history:",
            header=f"**Tracks:** {len(history)}\n"
                   f"**Time:** {utils.format_seconds(sum(track.length for track in history) // 1000, friendly=True)}\n\n",
            embed_footer=f"1 = most recent | {len(history)} = least recent"
        )

    @queue_history.command(name="detailed", aliases=["d"])
    @checks.is_queue_history_not_empty()
    @checks.is_voice_client_connected()
    async def queue_history_detailed(self, ctx: custom.Context) -> None:
        """
        Displays detailed information about the tracks in the queue history.
        """

        history = ctx.voice_client.queue._queue_history
        entries = []

        for track in history:

            embed = utils.embed(
                title=track.title,
                url=track.uri,
                description=f"**Author:** {track.author}\n"
                            f"**Length:** {utils.format_seconds(round(track.length) // 1000, friendly=True)}\n"
                            f"**Source:** {track.source.name.title()}\n"
                            f"**Requester:** {track.requester.mention} `{track.requester.id}`\n"
                            f"**Is stream:** {track.is_stream()}\n"
                            f"**Is seekable:** {track.is_seekable()}\n",
                image=track.thumbnail,
                footer=f"1 = most recent | {len(history)} = least recent"
            )
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    # Queue control commands

    @commands.command(name="clear", aliases=["clr"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def clear(self, ctx: custom.Context) -> None:
        """
        Clears the queue.
        """

        ctx.voice_client.queue.clear()
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="The queue has been cleared."))

    @commands.command(name="shuffle", aliases=["shfl"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def shuffle(self, ctx: custom.Context) -> None:
        """
        Shuffles the queue.
        """

        ctx.voice_client.queue.shuffle()
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="The queue has been shuffled."))

    @commands.command(name="reverse")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def reverse(self, ctx: custom.Context) -> None:
        """
        Reverses the queue.
        """

        ctx.voice_client.queue.reverse()
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description="The queue has been reversed."))

    @commands.command(name="sort")
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def sort(self, ctx: custom.Context, method: Literal["title", "length", "author"], reverse: bool = False) -> None:
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

        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description=f"The queue has been sorted by**{method}**."))

    @commands.command(name="remove", aliases=["rm"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def remove(self, ctx: custom.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        **entry**: The position of the track you want to remove.
        """

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That was not a valid track entry, try again with a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        item = ctx.voice_client.queue.get(entry - 1, put_history=False)
        await ctx.reply(embed=utils.embed(colour=colours.GREEN, description=f"Removed **[{item.title}]({item.uri})** by **{item.author}** from the queue."))

    @commands.command(name="move", aliases=["mv"])
    @checks.is_queue_not_empty()
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def move(self, ctx: custom.Context, entry_1: int = 0, entry_2: int = 0) -> None:
        """
        Move a track in the queue to a different position.

        **entry_1**: The position of the track you want to move from.
        **entry_2**: The position of the track you want to move too.
        """

        if entry_1 <= 0 or entry_1 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That was not a valid track entry to move from, try again with a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        if entry_2 <= 0 or entry_2 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"That was not a valid track entry to move too, try again with a number between **1** and **{len(ctx.voice_client.queue)}**.",
            )

        track = ctx.voice_client.queue.get(entry_1 - 1, put_history=False)
        ctx.voice_client.queue.put(track, position=entry_2 - 1)

        embed = utils.embed(
            colour=colours.GREEN,
            description=f"Moved **[{track.title}]({track.uri})** from position **{entry_1}** to position **{entry_2}**.",
        )
        await ctx.reply(embed=embed)

    # Effect commands

    @commands.command(name="8d", aliases=["8dimensional"])
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def _8d(self, ctx: custom.Context) -> None:
        """
        Sets an 8D audio filter on the player.
        """

        if enums.Filters.ROTATION in ctx.voice_client.enabled_filters:
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation())
            )
            ctx.voice_client.enabled_filters.remove(enums.Filters.ROTATION)
            embed = utils.embed(
                colour=colours.GREEN,
                description="**8D** audio effect is now **inactive**."
            )

        else:
            await ctx.voice_client.set_filter(
                slate.obsidian.Filter(ctx.voice_client.filter, rotation=slate.obsidian.Rotation(rotation_hertz=0.5))
            )
            ctx.voice_client.enabled_filters.add(enums.Filters.ROTATION)
            embed = utils.embed(
                colour=colours.GREEN,
                description="**8D** audio effect is now **active**."
            )

        await ctx.reply(embed=embed)

    @commands.command(name="night-core", aliases=["night_core", "nightcore", "nc"])
    @checks.is_author_connected()
    @checks.is_voice_client_connected()
    async def night_core(self, ctx: custom.Context) -> None:
        """
        Sets a nightcore audio filter on the player.
        """

        if enums.Filters.NIGHTCORE in ctx.voice_client.enabled_filters:
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale()))
            ctx.voice_client.enabled_filters.remove(enums.Filters.NIGHTCORE)
            embed = utils.embed(
                colour=colours.GREEN,
                description="**Nightcore** audio effect is now **inactive**."
            )

        else:
            await ctx.voice_client.set_filter(slate.obsidian.Filter(ctx.voice_client.filter, timescale=slate.obsidian.Timescale(speed=1.12, pitch=1.12)))
            ctx.voice_client.enabled_filters.add(enums.Filters.NIGHTCORE)
            embed = utils.embed(
                colour=colours.GREEN,
                description="**Nightcore** audio effect is now **active**."
            )

        await ctx.reply(embed=embed)

    # Debug commands

    @commands.is_owner()
    @commands.command(name="node-stats", aliases=["node_stats", "nodestats", "ns"], hidden=True)
    async def nodestats(self, ctx: custom.Context) -> None:
        """
        Displays information about the bots connected nodes.
        """

        embeds = []

        for node in self.bot.slate.nodes.values():

            embed = discord.Embed(
                colour=colours.MAIN,
                title=f"Stats: {node._identifier}",
                description=f"**Players:** {len(node.players.values())}\n"
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

    @commands.is_owner()
    @commands.command(name="voice-clients", aliases=["voice_clients", "voiceclients", "vcs"], hidden=True)
    async def voiceclients(self, ctx: custom.Context) -> None:
        """
        Displays information about voice clients that the bot has.
        """

        entries = []

        for node in self.bot.slate.nodes.values():
            for player in node.players.values():

                current = f"[{player.current.title}]({player.current.uri}) by **{player.current.author}**" if player.current else "None"
                position = \
                    f"{utils.format_seconds(player.position // 1000)} / {utils.format_seconds(player.current.length // 1000)}" \
                    if player.current \
                    else "N/A"

                entries.append(
                    f"**{player.channel.guild}:** `{player.channel.guild.id}`\n"
                    f"**Voice channel:** {player.voice_channel} `{getattr(player.voice_channel, 'id', None)}`\n"
                    f"**Text channel:** {player.text_channel} `{getattr(player.text_channel, 'id', None)}`\n"
                    f"**Track:** {current}\n"
                    f"**Position:** {position}\n"
                    f"**Queue length:** {len(player.queue)}\n"
                    f"**Is playing:** {player.is_playing()}\n"
                    f"**Is paused:** {player.is_paused()}\n"
                )

        if not entries:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="There are no active voice clients."
            )

        await ctx.paginate_embed(entries=entries, per_page=3)

    @commands.is_owner()
    @commands.command(name="voice-client", aliases=["voice_client", "voiceclient", "vc"], hidden=True)
    async def voiceclient(self, ctx: custom.Context, *, server: discord.Guild = utils.MISSING) -> None:
        """
        Displays information about a specific voice client.
        """

        guild = server or ctx.guild

        if not (player := self.bot.slate.players.get(guild.id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"**{guild}** does not have a voice client."
            )

        embed = utils.embed(
            title=f"{guild.name} `{guild.id}`",
            thumbnail=utils.icon(guild)
        )

        embed.add_field(
            name="__Player info:__",
            value=f"**Voice channel:** {player.voice_channel} `{getattr(player.voice_channel, 'id', None)}`\n"
                  f"**Text channel:** {player.text_channel} `{getattr(player.text_channel, 'id', None)}`\n"
                  f"**Is playing:** {player.is_playing()}\n"
                  f"**Is paused:** {player.is_paused()}\n",
            inline=False
        )

        if player.current:
            embed.add_field(
                name="__Track info:__",
                value=f"**Track:** [{player.current.title}]({player.current.uri})\n"
                      f"**Author:** {player.current.author}\n"
                      f"**Position:** {utils.format_seconds(player.position // 1000)} / {utils.format_seconds(player.current.length // 1000)}\n"
                      f"**Source:** {player.current.source.value.title()}\n"
                      f"**Requester:** {player.current.requester} `{player.current.requester.id}`\n"
                      f"**Is stream:** {player.current.is_stream()}\n"
                      f"**Is seekable:** {player.current.is_seekable()}\n",
                inline=False
            )
            embed.set_image(
                url=player.current.thumbnail
            )
        else:
            embed.add_field(
                name="__Track info:__",
                value=f"**Track:** None\n",
                inline=False
            )

        embed.add_field(
            name=f"__Queue info:__",
            value=f"**Length:** {len(player.queue)}\n"
                  f"**Total time:** {utils.format_seconds(sum(track.length for track in player.queue) // 1000, friendly=True)}\n"
                  f"**Loop mode:** {player.queue.loop_mode.name.title()}\n",
            inline=False
        )

        if not player.queue.is_empty():

            embed.add_field(
                name="__Up next:__",
                value="\n".join(
                    [f"**{index + 1}.** [{entry.title}]({entry.uri}) by **{entry.author}**" for index, entry in enumerate(list(player.queue)[:5])]
                ) + (f"\n ... **5** of **{len(player.queue)}** total." if len(player.queue) > 3 else ""),
                inline=False
            )

        embed.add_field(
            name="__Listeners:__",
            value="\n".join(
                f"- {member} `{member.id}`" for member in player.listeners[:5]
            ) + (f"\n ... **5** of **{len(player.listeners)}** total." if len(player.listeners) > 5 else ""),
            inline=False
        )

        await ctx.send(embed=embed)
