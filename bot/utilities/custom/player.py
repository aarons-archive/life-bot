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
import yarl

# My stuff
from core import colours, emojis
from utilities import custom, enums, exceptions, utils, views


if TYPE_CHECKING:

    # My stuff
    from core.bot import Life


class Player(slate.obsidian.Player["Life", custom.Context, "Player"]):

    def __init__(self, client: Life, channel: discord.VoiceChannel) -> None:
        super().__init__(client, channel)

        self._queue_add_event: asyncio.Event = asyncio.Event()
        self._track_end_event: asyncio.Event = asyncio.Event()

        self._task: asyncio.Task | None = None

        self._text_channel: discord.TextChannel | None = None
        self.message: discord.Message | None = None

        self.skip_request_ids: set[int] = set()
        self.enabled_filters: set[enums.Filters] = set()

        self.queue: custom.Queue = custom.Queue(self)

    @property
    def text_channel(self) -> discord.TextChannel | None:
        return self._text_channel

    @property
    def voice_channel(self) -> discord.VoiceChannel:
        return self.channel

    #

    async def invoke_controller(
        self,
        channel: discord.TextChannel | None = None
    ) -> discord.Message | None:

        if (channel is None and self.text_channel is None) or self.current is None:
            return

        text_channel = channel or self.text_channel
        if text_channel is None:
            return

        guild_config = await self.client.guild_manager.get_config(text_channel.guild.id)

        embed = utils.embed(
            title="Now playing:",
            description=f"**[{self.current.title}]({self.current.uri})**\nBy **{self.current.author}**",
            thumbnail=self.current.thumbnail
        )

        if guild_config.embed_size.value >= enums.EmbedSize.MEDIUM.value:

            embed.add_field(
                name="__Player info:__",
                value=f"**Paused:** {self.paused}\n"
                      f"**Loop mode:** {self.queue.loop_mode.name.title()}\n"
                      f"**Queue length:** {len(self.queue)}\n"
                      f"**Queue time:** {utils.format_seconds(sum(track.length for track in self.queue) // 1000, friendly=True)}\n",
            )
            embed.add_field(
                name="__Track info:__",
                value=f"**Time:** {utils.format_seconds(self.position // 1000)} / {utils.format_seconds(self.current.length // 1000)}\n"
                      f"**Is Stream:** {self.current.is_stream()}\n"
                      f"**Source:** {self.current.source.value.title()}\n"
                      f"**Requester:** {self.current.requester.mention if self.current.requester else 'N/A'}\n"
            )

        if guild_config.embed_size is enums.EmbedSize.LARGE and not self.queue.is_empty():

            entries = [f"**{index + 1}.** [{entry.title}]({entry.uri})" for index, entry in enumerate(list(self.queue)[:3])]
            if len(self.queue) > 3:
                entries.append(f"**...**\n**{len(self.queue)}.** [{self.queue[-1].title}]({self.queue[-1].uri})")

            embed.add_field(
                name="__Up next:__",
                value="\n".join(entries),
                inline=False
            )

        return await text_channel.send(embed=embed)

    async def send(
        self,
        *args, **kwargs
    ) -> None:

        if not self.text_channel:
            return

        await self.text_channel.send(*args, **kwargs)

    async def search(
        self,
        query: str,
        /,
        *,
        source: slate.Source,
        ctx: custom.Context,
    ) -> slate.obsidian.SearchResult[custom.Context]:

        if (url := yarl.URL(query)) and url.host and url.scheme:
            source = slate.Source.NONE

        try:
            search = await self._node.search(query, ctx=ctx, source=source)

        except slate.NoMatchesFound as error:

            if error.source:
                message = f"No {error.source.value.lower().replace('_', ' ')} {error.search_type.value}s were found for your search."
            else:
                message = f"No results were found for your search.",

            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=message,
            )

        except (slate.SearchError, slate.HTTPError):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="There was an error while searching for results.",
                view=views.SupportButton()
            )

        return search

    async def queue_search(
        self,
        query: str,
        /,
        *,
        source: slate.Source,
        ctx: custom.Context,
        now: bool = False,
        next: bool = False,
        choose: bool = False,
    ) -> None:

        search = await self.search(query, source=source, ctx=ctx)

        if choose:
            choice = await ctx.choice(
                entries=[f"`{index + 1:}.` [{track.title}]({track.uri})" for index, track in enumerate(search.tracks)],
                per_page=10,
                title="Select the number of the track you want to play:",
            )
            tracks = search.tracks[choice]
        else:
            tracks = search.tracks[0] if search.type is slate.SearchType.TRACK else search.tracks

        self.queue.put(tracks, position=0 if (now or next) else None)
        if now:
            await self.stop()

        if search.type is slate.SearchType.TRACK or isinstance(search.result, list):
            description = f"Added the {search.source.value.lower()} track [{search.tracks[0].title}]({search.tracks[0].uri}) to the queue."
        else:
            description = f"Added the {search.source.value.lower()} {search.type.name.lower()} [{search.result.name}]({search.result.uri}) to the queue."

        await ctx.reply(embed=utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=description))

    #

    async def loop(self) -> None:

        while True:

            self._queue_add_event.clear()
            self._track_end_event.clear()

            if self.queue.is_empty():

                try:
                    with async_timeout.timeout(timeout=3600):
                        await self._queue_add_event.wait()
                except asyncio.TimeoutError:
                    await self.disconnect()
                    break

            track = self.queue.get()

            if track.source is slate.Source.SPOTIFY:

                try:
                    search = await self.search(f"{track.author} - {track.title}", source=slate.Source.YOUTUBE, ctx=track.ctx)
                except exceptions.EmbedError as error:
                    await self.send(embed=error.embed)
                    continue

                track = search.tracks[0]

            await self.play(track)

            await self._track_end_event.wait()

    #

    async def connect(self, *, timeout: float | None = None, reconnect: bool | None = None, self_deaf: bool = True) -> None:

        await super().connect(timeout=timeout, reconnect=reconnect, self_deaf=self_deaf)
        self._task = asyncio.create_task(self.loop())

    async def disconnect(self, *, force: bool = False) -> None:

        await super().disconnect(force=force)

        if self._task is not None and self._task.done() is False:
            self._task.cancel()

    #

    async def handle_track_start(self) -> None:
        self.message = await self.invoke_controller()

    async def handle_track_over(self) -> None:

        self.skip_request_ids = set()
        self._current = None

        self._track_end_event.set()
        self._track_end_event.clear()

        if not self.message:
            return

        try:
            old = self.queue._queue_history[0]
        except IndexError:
            return

        await self.message.edit(embed=utils.embed(description=f"Finished playing **[{old.title}]({old.uri})** by **{old.author}**."))

    async def handle_track_error(self) -> None:

        await self.send(
            embed=utils.embed(
                colour=colours.RED,
                description=f"Something went wrong while playing a track.",
            ),
            view=views.SupportButton()
        )

        await self.handle_track_over()
