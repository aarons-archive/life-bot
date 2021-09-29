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
from core import colours, config, emojis
from utilities import context, enums, exceptions, utils


if TYPE_CHECKING:

    # My stuff
    from core.bot import Life


class Queue(slate.Queue[slate.obsidian.Track]):

    def __init__(self, player: Player, /) -> None:

        super().__init__()
        self.player: Player = player

    #

    def put(
        self,
        items: list[slate.obsidian.Track[context.Context[Life]]] | slate.obsidian.Track[context.Context[Life]],
        /,
        *,
        position: int | None = None
    ) -> None:

        super().put(items, position=position)

        self.player._queue_add_event.set()
        self.player._queue_add_event.clear()


class Player(slate.obsidian.Player["Life", context.Context[Life], "Player"]):

    def __init__(
        self,
        client: Life,
        channel: discord.VoiceChannel
    ) -> None:
        super().__init__(client, channel)

        self._queue_add_event: asyncio.Event = asyncio.Event()
        self._track_start_event: asyncio.Event = asyncio.Event()
        self._track_end_event: asyncio.Event = asyncio.Event()

        self._queue: Queue = Queue(self)

        self._text_channel: discord.TextChannel | None = None
        self._task: asyncio.Task | None = None

        self.skip_request_ids: set[int] = set()
        self.enabled_filters: set[enums.Filters] = set()

    @property
    def queue(self) -> Queue:
        return self._queue

    @property
    def text_channel(self) -> discord.TextChannel | None:
        return self._text_channel

    @property
    def voice_channel(self) -> discord.VoiceChannel:
        return self.channel

    #

    async def invoke_controller(self) -> None:

        if not self.current:
            return

        embed = discord.Embed(
            colour=colours.MAIN,
            title="Now playing:",
            description=f"**[{self.current.title}]({self.current.uri})**"
        ).set_thumbnail(
            url=self.current.thumbnail
        )

        guild_config = await self.client.guild_manager.get_config(self.current.ctx.guild.id)

        if guild_config.embed_size is enums.EmbedSize.LARGE:

            embed.add_field(
                name="Player info:",
                value=f"`Paused:` {self.paused}\n"
                      f"`Loop mode:` {self.queue.loop_mode.name.title()}\n"
                      f"`Filter:` {getattr(self.filter, 'name', None)}\n"
                      f"`Queue entries:` {len(self.queue)}\n"
                      f"`Queue time:` {utils.format_seconds(sum(track.length for track in self.queue) // 1000, friendly=True)}\n",
            ).add_field(
                name="Track info:",
                value=f"`Time:` {utils.format_seconds(self.position // 1000)} / {utils.format_seconds(seconds=self.current.length // 1000)}\n"
                      f"`Author:` {self.current.author}\n"
                      f"`Source:` {self.current.source.value.title()}\n"
                      f"`Requester:` {self.current.requester.mention}\n"
                      f"`Seekable:` {self.current.is_seekable()}\n",
            )

            if not self.queue.is_empty():

                entries = [f"`{index + 1}.` [{entry.title}]({entry.uri})" for index, entry in enumerate(list(self.queue)[:5])]
                if len(self.queue) > 5:
                    entries.append(f"`...`\n`{len(self.queue)}.` [{self.queue[-1].title}]({self.queue[-1].uri})")

                embed.add_field(name="Up next:", value="\n".join(entries), inline=False)

        elif guild_config.embed_size is enums.EmbedSize.MEDIUM:

            embed.add_field(
                name="Player info:",
                value=f"`Paused:` {self.paused}\n"
                      f"`Loop mode:` {self.queue.loop_mode.name.title()}\n"
                      f"`Filter:` {getattr(self.filter, 'name', None)}\n",
            ).add_field(
                name="Track info:",
                value=f"`Time:` {utils.format_seconds(seconds=self.position // 1000)} / {utils.format_seconds(seconds=self.current.length // 1000)}\n"
                      f"`Author:` {self.current.author}\n"
                      f"`Source:` {self.current.source.value.title()}\n",
            )

        await self.send(embed=embed)

    async def send(self, *args, **kwargs) -> None:

        if not self.text_channel:
            return

        await self.text_channel.send(*args, **kwargs)

    #

    async def search(
        self,
        query: str,
        ctx: context.Context[Life],
        source: slate.Source
    ) -> slate.obsidian.SearchResult[context.Context[Life]] | None:

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
        ctx: context.Context[Life],
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
                    await self.send(
                        embed=utils.embed(
                            colour=colours.RED,
                            emoji=emojis.CROSS,
                            description="Nothing was added to the queue for two minutes, cya next time!",
                        )
                    )
                    await self.disconnect()
                    break

            track = self.queue.get()

            if track.source is slate.Source.SPOTIFY:

                try:
                    search = await self.search(query=f"{track.author} - {track.title}", ctx=track.ctx, source=slate.Source.YOUTUBE_MUSIC)
                except exceptions.EmbedError:
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
                await self.send(
                    embed=utils.embed(
                        colour=colours.RED,
                        emoji=emojis.CROSS,
                        description=f"There was an error while playing the track [{self.current.title}]({self.current.uri}).",
                    )
                )
                continue

            await self.invoke_controller()

            await self._track_end_event.wait()

            self._current = None
