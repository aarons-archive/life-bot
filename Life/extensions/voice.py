from __future__ import annotations

import math
from typing import Literal, Optional

import discord
import ksoftapi
import slate
from discord.ext import commands
from slate import obsidian

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


class Voice(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    #

    async def load(self) -> None:

        for node in config.NODES:
            try:
                await self.bot.slate.create_node(
                    type=obsidian.ObsidianNode,
                    bot=self.bot,
                    host=node["host"],
                    port=node["port"],
                    password=node["password"],
                    identifier=node["identifier"],
                    region=discord.VoiceRegion.us_east,
                    spotify_client_id=config.SPOTIFY_CLIENT_ID,
                    spotify_client_secret=config.SPOTIFY_CLIENT_SECRET
                )
            except slate.NodeConnectionError:
                continue

    # Events

    @commands.Cog.listener()
    async def on_obsidian_track_start(self, player: custom.Player, _: obsidian.ObsidianTrackStart) -> None:

        player._track_start_event.set()
        player._track_start_event.clear()

    @commands.Cog.listener()
    async def on_obsidian_track_end(self, player: custom.Player, _: obsidian.ObsidianTrackEnd) -> None:

        player._track_end_event.set()
        player._track_end_event.clear()

        player.skip_request_ids = set()

    @commands.Cog.listener()
    async def on_obsidian_track_exception(self, player: custom.Player, event: obsidian.ObsidianTrackException) -> None:

        track = None
        try:
            track = await player.node.decode_track(track_id=event.track_id)
        except slate.HTTPError:
            pass

        title = getattr(track or player.current, "title", "Not Found")
        await player.send(f"There was an error of severity **{event.severity}** while playing the track **{title}**.\nReason: {event.message}")

        player._track_end_event.set()
        player._track_end_event.clear()

        player.skip_request_ids = set()

    @commands.Cog.listener()
    async def on_obsidian_track_stuck(self, player: custom.Player, event: obsidian.ObsidianTrackStuck) -> None:

        track = None
        try:
            track = await player.node.decode_track(track_id=event.track_id)
        except slate.HTTPError:
            pass

        title = getattr(track or player.current, "title", "Not Found")
        await player.send(f"Something went wrong while playing the track **{title}**. Use **{config.PREFIX}support** for more help.")

        player._track_end_event.set()
        player._track_end_event.clear()

        player.skip_request_ids = set()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, _: discord.VoiceState, __: discord.VoiceState) -> None:

        if member.bot:
            return

        if not (guild := self.bot.get_guild(member.guild.id)):
            return

        # noinspection PyTypeChecker
        voice_client: custom.Player = guild.voice_client
        if not voice_client:
            return

        if not [member for member in voice_client.voice_channel.members if not member.bot] and (not voice_client.paused):

            await voice_client.set_pause(True)

            embed = utils.embed(
                colour=colours.RED,
                emoji=emojis.PAUSED,
                description=f"The player is now **paused** because there is no one in {voice_client.voice_channel.mention}."
            )
            await voice_client.send(embed=embed)
            return

        if all(member.voice.self_deaf or member.voice.deaf for member in voice_client.voice_channel.members if not member.bot) and (not voice_client.paused):

            await voice_client.set_pause(True)

            embed = utils.embed(
                colour=colours.RED,
                emoji=emojis.PAUSED,
                description=f"The player is now **paused** because everyone in {voice_client.voice_channel.mention} is deafened."
            )
            await voice_client.send(embed=embed)
            return

        if voice_client.paused:

            await voice_client.set_pause(False)

            embed = utils.embed(
                colour=colours.RED,
                emoji=emojis.PLAYING,
                description="The player is now **resumed** as at least one person is listening."
            )
            await voice_client.send(embed=embed)

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
                description=f"I am already connected to {ctx.voice_client.voice_channel.mention}."
            )

        # noinspection PyTypeChecker
        await ctx.author.voice.channel.connect(cls=custom.Player)
        ctx.voice_client._text_channel = ctx.channel

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Joined {ctx.voice_client.voice_channel.mention}."
        )
        await ctx.send(embed=embed)

    @commands.command(name="disconnect", aliases=["dc", "leave", "destroy"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def disconnect(self, ctx: context.Context) -> None:
        """
        Disconnects the bot its voice channel.
        """

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Left {ctx.voice_client.voice_channel.mention}."
        )
        await ctx.send(embed=embed)

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
        **--music**: Searches [youtube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-play If I Can't Have You by Shawn Mendes --now`
        `l-play Senorita by Shawn Mendes --next`
        `l-play Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=get_source(options))

    @commands.command(name="search")
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def search(self, ctx: context.Context, query: str, *, options: Options) -> None:
        """
        Choose which track to play based on a search.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [youtube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-search If I Can't Have You by Shawn Mendes --now`
        `l-search Senorita by Shawn Mendes --next`
        `l-search Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=get_source(options), choose=True)

    # Platform specific play commands

    @commands.command(name="youtubemusic", aliases=["youtube-music", "youtube_music", "ytmusic", "yt-music", "yt_music", "ytm"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def youtube_music(self, ctx: context.Context, query: str, *, options: QueueOptions) -> None:
        """
        Queues tracks from youtube music with the given name or url.

        **query**: The query to search for tracks with.

        **Flags:**
        **--next**: Puts the track that is found at the start of the queue.
        **--now**: Skips the current track and plays the track that is found.

        **Usage:**
        `l-youtube-music Lost In Japan by Shawn Mendes --now`
        `l-ytm If I Can't Have You by Shawn Mendes --next`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.YOUTUBE_MUSIC)

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
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.SOUNDCLOUD)

    # Queue specific play commands

    @commands.command(name="playnext", aliases=["play-next", "play_next", "pnext"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play_next(self, ctx: context.Context, query: str, *, options: SearchOptions) -> None:
        """
        Queues tracks at the start of the queue.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [youtube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.

        **Usage:**
        `l-play-next Lost In Japan by Shawn Mendes --music`
        `l-pnext If I Can't Have You by Shawn Mendes --soundcloud`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, next=True, source=get_source(options))

    @commands.command(name="playnow", aliases=["play-now", "play_now", "pnow"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play_now(self, ctx: context.Context, query: str, *, options: SearchOptions) -> None:
        """
        Queues tracks and skips the current track.

        **query**: The query to search for tracks with.

        **Flags:**
        **--music**: Searches [youtube music](https://music.youtube.com/) for results.
        **--soundcloud**: Searches [soundcloud](https://soundcloud.com/) for results.

        **Usage:**
        `l-play-now Lost In Japan by Shawn Mendes --music`
        `l-pnow If I Can't Have You by Shawn Mendes --soundcloud`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=True, source=get_source(options))

    # Pause/Resume commands

    @commands.command(name="pause", aliases=["stop"])
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def pause(self, ctx: context.Context) -> None:
        """
        Pauses the current track.
        """

        if ctx.voice_client.paused:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The player is already paused."
            )

        await ctx.voice_client.set_pause(True)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.PAUSED,
            description="The player is now **paused**."
        )
        await ctx.reply(embed=embed)

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

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.PLAYING,
            description="The player is now **resumed**."
        )
        await ctx.reply(embed=embed)

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
                            f"**{utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}**."
            )

        await ctx.voice_client.set_position(milliseconds)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.SEEK_FORWARD,
            description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

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
                description=f"That is not a valid amount of time. Please choose an amount lower than **{utils.format_seconds(remaining // 1000, friendly=True)}**."
            )

        await ctx.voice_client.set_position(position + milliseconds)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.SEEK_FORWARD,
            description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

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
                description=f"That is not a valid amount of time. Please choose an amount lower than **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
            )

        await ctx.voice_client.set_position(position - milliseconds)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.SEEK_BACK,
            description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

    @commands.command(name="replay")
    @checks.is_track_seekable()
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def replay(self, ctx: context.Context) -> None:
        """
        Seeks to the start of the current track.
        """

        await ctx.voice_client.set_position(position=0)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.REPEAT,
            description=f"The players position is now **{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}**."
        )
        await ctx.reply(embed=embed)

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

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.LOOP_CURRENT,
            description=f"The queue looping mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**."
        )
        await ctx.reply(embed=embed)

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

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.LOOP,
            description=f"The queue looping mode is now **{ctx.voice_client.queue.loop_mode.name.title()}**."
        )
        await ctx.reply(embed=embed)

    # Skip commands

    @commands.command(name="skip", aliases=["next", "s", "voteskip", "vote-skip", "vote_skip", "vs", "forceskip", "force-skip", "force_skip", "fs", "skipto"])
    @checks.is_voice_client_playing()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def skip(self, ctx: context.Context, amount: int = 1) -> None:
        """
        Votes to skip the current track.
        """

        try:
            await commands.check_any(
                commands.is_owner(), checks.is_guild_owner(), checks.is_track_requester(),
                checks.has_any_permissions(manage_guild=True, kick_members=True, ban_members=True, manage_messages=True, manage_channels=True)
            ).predicate(ctx=ctx)

        except commands.CheckAnyFailure:

            if ctx.author not in ctx.voice_client.listeners:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You can not vote to skip as you are currently deafened."
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
                    description=f"{message} currently on **{len(ctx.voice_client.skip_request_ids)}** out of **{skips_needed}** votes needed to skip."
                )

            await ctx.voice_client.stop()

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.NEXT,
                description="Skipped the current track."
            )
            await ctx.reply(embed=embed)
            return

        if 0 <= amount > len(ctx.voice_client.queue) + 1:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are not enough tracks in the queue to skip that many. Choose a number between **1** and **{len(ctx.voice_client.queue) + 1}**."
            )

        for track in ctx.voice_client.queue[:amount - 1]:
            try:
                if track.requester.id != ctx.author.id:
                    raise commands.CheckAnyFailure(checks=[], errors=[])
                await commands.check_any(
                    commands.is_owner(), checks.is_guild_owner(),
                    checks.has_any_permissions(manage_guild=True, kick_members=True, ban_members=True, manage_messages=True, manage_channels=True)
                ).predicate(ctx=ctx)
            except commands.CheckAnyFailure:
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"You do not have permission to skip the next **{amount}** tracks in the queue."
                )

        for _ in enumerate(ctx.voice_client.queue[:amount - 1]):
            ctx.voice_client.queue.get()

        await ctx.voice_client.stop()

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.NEXT,
            description=f"Skipped **{amount}** track{'s' if amount != 1 else ''}."
        )
        await ctx.reply(embed=embed)

    # Misc

    @commands.command(name="nowplaying", aliases=["np"])
    @checks.is_voice_client_playing()
    @checks.has_voice_client(try_join=False)
    async def nowplaying(self, ctx: context.Context) -> None:
        """
        Shows the player controller.
        """

        await ctx.voice_client.invoke_controller()

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
                            f"**Seekable:** {ctx.voice_client.current.is_seekable()}"
            ).set_image(
                url=ctx.voice_client.current.thumbnail
            )
            await ctx.author.send(embed=embed)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="Saved the current track to our DM's."
            )
            await ctx.reply(embed=embed)

        except discord.Forbidden:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="I am unable to DM you."
            )

    @commands.command(name="lyrics", aliases=["ly"])
    async def lyrics(self, ctx: context.Context, *, query: Optional[str]) -> None:
        """
        Displays lyrics for the given song.

        **query**: The query to search for lyrics with, If not provided the bot will try to display lyrics for the song you are listening to on spotify, or the track playing in a voice chat the bot is in.

        You can also force it to display lyrics from either of these by specifying the **query** argument as **spotify** or **player**.
        """

        def get_spotify_query() -> Optional[str]:

            if not (activity := discord.utils.find(lambda a: isinstance(a, discord.Spotify), ctx.author.activities)):
                return None

            featuring = f" feat.{' & '.join(activity.artists[1:])}" if len(activity.artists) > 1 else ""
            return f"{activity.artist[:activity.artist.index(';')] if len(activity.artists) > 1 else activity.artist}{featuring} - {activity.title}"

        def get_player_query() -> Optional[str]:

            if not ctx.voice_client or ctx.voice_client.is_playing() is False:
                return None

            return f"{ctx.voice_client.current.author} - {ctx.voice_client.current.title}"

        if query == "spotify":
            if not (query := get_spotify_query()):
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You don't have an active spotify status to fetch lyrics from."
                )

        elif query == "player":
            if not (query := get_player_query()):
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="I am not playing a track in voice chat to fetch lyrics from."
                )

        else:
            if query is None and not (query := get_spotify_query()) and not (query := get_player_query()):
                raise exceptions.EmbedError(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description="You must provide a search term to find lyrics for."
                )

        try:
            results = await self.bot.ksoft.music.lyrics(query, limit=50)
        except ksoftapi.NoResults:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"No results were found for the search **{query}**."
            )
        except ksoftapi.APIError:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The API used to fetch lyrics is currently unavailable."
            )

        choice = await ctx.choice(
            entries=[f"`{index + 1}:` {result.artist} - {result.name}" for index, result in enumerate(results)],
            per_page=10,
            title="Type the number of the song that you want lyrics for:",
            header=f"**Query:** {query}\n\n"
        )
        result = results[choice]

        entries = []
        for line in result.lyrics.split("\n"):

            if not entries:
                entries.append(line)
                continue

            last_entry = entries[-1]
            if len(last_entry) >= 1000 or len(last_entry) + len(line) >= 1000:
                entries.append(line)
                continue

            entries[-1] += f"\n{line}"

        await ctx.paginate_embed(
            entries=entries,
            per_page=1,
            title=f"Lyrics for **{result.name}** by **{result.artist}**:",
            embed_footer="Lyrics provided by KSoft.Si API"
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
                   f"**Total time:** {utils.format_seconds(sum(track.length for track in ctx.voice_client.queue) // 1000, friendly=True)}\n\n"
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
                            f"**Source:** {track.source.name.title()}\n" \
                            f"**Length:** {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}\n" \
                            f"**Live:** {track.is_stream()}\n"
                            f"**Seekable:** {track.is_seekable()}\n"
                            f"**Requester:** {track.requester.mention}"
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
                   f"**Total time:** {utils.format_seconds(sum(track.length for track in history) // 1000, friendly=True)}\n\n"
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
                            f"**Source:** {track.source.name.title()}\n" \
                            f"**Length:** {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}\n" \
                            f"**Live:** {track.is_stream()}\n"
                            f"**Seekable:** {track.is_seekable()}\n"
                            f"**Requester:** {track.requester.mention}"
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

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description="The queue has been cleared."
        )
        await ctx.reply(embed=embed)

    @commands.command(name="shuffle")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def shuffle(self, ctx: context.Context) -> None:
        """
        Shuffles the queue.
        """

        ctx.voice_client.queue.shuffle()

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.SHUFFLE,
            description="The queue has been shuffled."
        )
        await ctx.reply(embed=embed)

    @commands.command(name="reverse")
    @checks.queue_not_empty()
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def reverse(self, ctx: context.Context) -> None:
        """
        Reverses the queue.
        """

        ctx.voice_client.queue.reverse()

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.DOUBLE_LEFT,
            description="The queue has been reversed."
        )
        await ctx.reply(embed=embed)

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

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"The queue has been sorted with method **{method}**."
        )
        await ctx.reply(embed=embed)

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
                description=f"That was not a valid track entry. Choose a number between **1** and **{len(ctx.voice_client.queue)}**."
            )

        item = ctx.voice_client.queue.get(position=entry - 1, put_history=False)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Removed **[{item.title}]({item.uri})** from the queue."
        )
        await ctx.reply(embed=embed)

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
                description=f"That was not a valid track entry to move from. Choose a number between **1** and **{len(ctx.voice_client.queue)}**."
            )

        if entry_2 <= 0 or entry_2 > len(ctx.voice_client.queue):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"That was not a valid track entry to move too. Choose a number between **1** and **{len(ctx.voice_client.queue)}**."
            )

        track = ctx.voice_client.queue.get(position=entry_1 - 1, put_history=False)
        ctx.voice_client.queue.put(items=track, position=entry_2 - 1)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description=f"Moved **[{track.title}]({track.uri})** from position **{entry_1}** to position **{entry_2}**."
        )
        await ctx.reply(embed=embed)

    # Effect commands

    @commands.command(name="8d")
    @checks.is_author_connected(same_channel=True)
    @checks.has_voice_client(try_join=False)
    async def _8d(self, ctx: context.Context) -> None:
        """
        Sets an 8D audio filter on the player.
        """

        if enums.Filters.ROTATION in ctx.voice_client.enabled_filters:
            await ctx.voice_client.set_filter(obsidian.Filter(filter=ctx.voice_client.filter, rotation=obsidian.Rotation()))
            ctx.voice_client.enabled_filters.remove(enums.Filters.ROTATION)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**8D** audio effect is now **inactive**."
            )
        else:
            await ctx.voice_client.set_filter(obsidian.Filter(filter=ctx.voice_client.filter, rotation=obsidian.Rotation(rotation_hertz=0.5)))
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
            await ctx.voice_client.set_filter(obsidian.Filter(filter=ctx.voice_client.filter, timescale=obsidian.Timescale()))
            ctx.voice_client.enabled_filters.remove(enums.Filters.NIGHTCORE)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**Nightcore** audio effect is now **inactive**."
            )
        else:
            await ctx.voice_client.set_filter(obsidian.Filter(filter=ctx.voice_client.filter, timescale=obsidian.Timescale(speed=1.12, pitch=1.12)))
            ctx.voice_client.enabled_filters.add(enums.Filters.NIGHTCORE)

            embed = utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description="**Nightcore** audio effect is now **active**."
            )
        await ctx.reply(embed=embed)


def setup(bot: Life) -> None:
    bot.add_cog(Voice(bot=bot))
