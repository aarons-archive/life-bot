# Future
from __future__ import annotations

# Standard Library
import asyncio
from typing import TYPE_CHECKING

# Packages
import async_timeout
import discord
import slate
import slate.obsidian

# My stuff
from core import colours, config, emojis, values
from utilities import context, custom, enums, exceptions, utils


if TYPE_CHECKING:

    # My stuff
    from core.bot import Life


class Player(slate.obsidian.Player["Life", context.Context, "Player"]):

    def __init__(
        self,
        client: Life,
        channel: discord.VoiceChannel
    ) -> None:
        super().__init__(client, channel)

        self._queue_add_event: asyncio.Event = asyncio.Event()
        self._track_start_event: asyncio.Event = asyncio.Event()
        self._track_end_event: asyncio.Event = asyncio.Event()

        self._task: asyncio.Task | None = None

        self._text_channel: discord.TextChannel | None = None

        self.skip_request_ids: set[int] = set()
        self.enabled_filters: set[enums.Filters] = set()

        self.queue: custom.Queue = custom.Queue(self)
        self.controller: custom.Controller = custom.Controller(self)

    @property
    def text_channel(self) -> discord.TextChannel | None:
        return self._text_channel

    @property
    def voice_channel(self) -> discord.VoiceChannel:
        return self.channel

    #

    async def search(
        self,
        query: str,
        ctx: context.Context,
        source: slate.Source
    ) -> slate.obsidian.SearchResult[context.Context] | None:

        try:
            search = await self._node.search(query, ctx=ctx, source=source)

        except (slate.HTTPError, slate.obsidian.SearchError):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="There was an error while searching for results."
            )
        except slate.NoMatchesFound as error:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"No {error.source.value.lower().replace('_', ' ')} {error.search_type.value}s were found for your query.",
            )

        if search.source in [slate.Source.HTTP, slate.Source.LOCAL] and ctx.author.id not in config.OWNER_IDS:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="You do not have permission to play tracks from `HTTP` or `LOCAL` sources.",
            )

        return search

    async def queue_search(
        self,
        query: str,
        ctx: context.Context,
        source: slate.Source,
        now: bool = False,
        next: bool = False,
        choose: bool = False,
    ) -> None:

        search = await self.search(query, ctx=ctx, source=source)

        if choose:
            choice = await ctx.choice(
                entries=[f"`{index + 1:}:` [{track.title}]({track.uri})" for index, track in enumerate(search.tracks)],
                per_page=10,
                title="Select the number of the track you want to play:",
            )
            tracks = search.tracks[choice]
        else:
            tracks = search.tracks[0] if search.type is slate.SearchType.TRACK else search.tracks

        self.queue.put(
            tracks,
            position=0 if (now or next) else None
        )
        if now:
            await self.stop()

        if search.type is slate.SearchType.TRACK or isinstance(search.result, list):
            description = f"Added the {search.source.value.lower()} track [{search.tracks[0].title}]({search.tracks[0].uri}) to the queue."
        else:
            description = f"Added the {search.source.value.lower()} {search.type.name.lower()} [{search.result.name}]({search.result.url}) to the queue."

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN, emoji=emojis.TICK, description=description
            )
        )

    #

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_deaf: bool = True
    ) -> None:

        await super().connect(timeout=timeout, reconnect=reconnect, self_deaf=self_deaf)
        self._task = asyncio.create_task(self.loop())

    async def disconnect(
        self,
        *,
        force: bool = False
    ) -> None:

        await super().disconnect(force=force)
        self._task.cancel()

    #

    async def send(self, *args, **kwargs) -> None:

        if not self.text_channel:
            return

        await self.text_channel.send(*args, **kwargs)

    async def loop(self) -> None:

        while True:

            self._queue_add_event.clear()
            self._track_start_event.clear()
            self._track_end_event.clear()

            if self.queue.is_empty():

                try:
                    with async_timeout.timeout(timeout=120):
                        await self._queue_add_event.wait()

                except asyncio.TimeoutError:

                    embed = utils.embed(
                        colour=colours.RED,
                        description="Nothing was added to the queue for two minutes, cya next time!",
                    )
                    await self.send(embed=embed)
                    await self.disconnect()
                    break

            track = self.queue.get()

            if track.source is slate.Source.SPOTIFY:

                try:
                    search = await self.search(query=f"{track.author} - {track.title}", ctx=track.ctx, source=slate.Source.YOUTUBE)
                except exceptions.EmbedError as error:
                    await self.send(embed=error.embed)
                    continue

                track = search.tracks[0]

            await self.play(track)

            try:
                with async_timeout.timeout(timeout=5):
                    await self._track_start_event.wait()

            except asyncio.TimeoutError:
                embed = utils.embed(
                    colour=colours.RED,
                    emoji=emojis.CROSS,
                    description=f"There was an error while playing the track [{self.current.title}]({self.current.uri}).",
                )
                await self.send(embed=embed)
                continue

            await self._track_end_event.wait()

    #

    async def _handle_track_error(self) -> None:

        embed = utils.embed(
            colour=colours.RED,
            description=f"Something went wrong while playing a track. "
                        f"Join my [support server]({values.SUPPORT_LINK}) for more help.",
        )
        await self.send(embed=embed)

        await self._handle_track_over()

    async def _handle_track_over(self) -> None:

        self._track_end_event.set()
        self._track_end_event.clear()

        self._skip_request_ids = set()

        await self.controller.edit_old()
