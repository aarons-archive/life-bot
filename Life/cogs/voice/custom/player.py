"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import asyncio
import logging
import textwrap
from typing import Optional

import async_timeout
import discord

import config
import emoji
import slate
from bot import Life
from cogs.voice.custom.queue import Queue
from slate import obsidian
from utilities import context, enums, exceptions, utils


__all__ = ['Player']
__log__ = logging.getLogger('slate.obsidian.player')


class Player(obsidian.ObsidianPlayer):

    def __init__(self, bot: Life, channel: discord.VoiceChannel) -> None:
        super().__init__(bot, channel)

        self._text_channel: Optional[discord.TextChannel] = None
        self._dj: Optional[discord.Member] = None

        self._queue: Queue = Queue(player=self)

        self._queue_add_event: asyncio.Event = asyncio.Event()
        self._track_start_event: asyncio.Event = asyncio.Event()
        self._track_end_event: asyncio.Event = asyncio.Event()

        self._task: Optional[asyncio.Task] = None

    def __repr__(self) -> str:
        return f'<life.Player>'

    #

    @property
    def text_channel(self) -> Optional[discord.TextChannel]:
        return self._text_channel

    @property
    def voice_channel(self) -> Optional[discord.VoiceChannel]:
        return self.channel

    @property
    def dj(self) -> Optional[discord.Member]:
        return self._dj

    @property
    def queue(self) -> Queue:
        return self._queue

    #

    async def connect(self, *, timeout: Optional[float] = None, reconnect: Optional[bool] = None, self_deaf: bool = True) -> None:

        await super().connect(timeout=timeout, reconnect=reconnect, self_deaf=self_deaf)
        self._task = asyncio.create_task(self.loop())

    async def disconnect(self, *, force: bool = False) -> None:

        await super().disconnect(force=force)
        self._task.cancel()

    #

    async def loop(self) -> None:

        while True:

            self._queue_add_event.clear()
            self._track_start_event.clear()
            self._track_end_event.clear()

            if self.queue.is_empty:

                try:
                    with async_timeout.timeout(timeout=120):
                        await self._queue_add_event.wait()
                except asyncio.TimeoutError:
                    await self.send(embed=discord.Embed(colour=config.MAIN, description=f'{emoji.CROSS}  Nothing was added to the queue for 2 minutes, cya!'))
                    await self.disconnect()
                    break

            track = self.queue.get()

            if track.source is slate.Source.SPOTIFY:

                try:
                    search = await self.search(query=f'{track.author} - {track.title}', ctx=track.ctx, source=slate.Source.YOUTUBE_MUSIC)
                except exceptions.VoiceError:
                    try:
                        search = await self.search(query=f'{track.author} - {track.title}', ctx=track.ctx, source=slate.Source.YOUTUBE)
                    except exceptions.VoiceError as error:
                        await self.send(embed=discord.Embed(colour=config.MAIN, description=f'{emoji.UNKNOWN}  {error}'))
                        continue

                track = search.tracks[0]

            await self.play(track)

            try:
                with async_timeout.timeout(timeout=5):
                    await self._track_start_event.wait()
            except asyncio.TimeoutError:
                await self.send(embed=discord.Embed(colour=config.MAIN, description=f'{emoji.CROSS}  There was an error while playing the track [{self.current.title}]({self.current.uri}).'))
                continue

            await self._track_end_event.wait()

            self._current = None

    #

    async def invoke_controller(self) -> None:

        embed = discord.Embed(colour=config.MAIN, title='Now playing:', description=f'**[{self.current.title}]({self.current.uri})**')
        embed.set_thumbnail(url=self.current.thumbnail)

        if self.current.ctx.guild_config.embed_size is enums.EmbedSize.LARGE:

            embed.add_field(
                    name='Player info:',
                    value=textwrap.dedent(
                            f'''
                            `Paused:` {self.paused}
                            `Loop mode:` {self.queue.loop_mode.name.title()}
                            `Filter:` {getattr(self.filter, "name", None)}
                            `Queue entries:` {len(self.queue)}
                            `Queue time:` {utils.format_seconds(seconds=round(sum(track.length for track in self.queue)) // 1000, friendly=True)}
                            '''
                    )
            )
            embed.add_field(
                    name='Track info:',
                    value=textwrap.dedent(
                            f'''
                            `Time:` {utils.format_seconds(seconds=round(self.position) // 1000)} / {utils.format_seconds(seconds=round(self.current.length) // 1000)}
                            `Author:` {self.current.author}
                            `Source:` {self.current.source.value.title()}
                            `Requester:` {self.current.requester.mention}
                            `Seekable:` {self.current.is_seekable}
                            '''
                    )
            )

            if not self.queue.is_empty:

                entries = [f'`{index + 1}.` [{entry.title}]({entry.uri}) | {utils.format_seconds(entry.length // 1000)} | {entry.requester.mention}' for index, entry in enumerate(self.queue[:5])]
                if len(self.queue) > 5:
                    entries.append(
                            f'`...`\n`{len(self.queue)}.` [{self.queue[-1].title}]({self.queue[-1].uri}) | {utils.format_seconds(self.queue[-1].length // 1000)} | {self.queue[-1].requester.mention}'
                    )

                embed.add_field(name='Up next:', value='\n'.join(entries), inline=False)

        elif self.current.ctx.guild_config.embed_size is enums.EmbedSize.MEDIUM:

            embed.add_field(
                    name='Player info:',
                    value=f'''
                    `Paused:` {self.paused}
                    `Loop mode:` {self.queue.loop_mode.value.title()}
                    `Filter:` {getattr(self.filter, "name", None)}
                    '''
            )
            embed.add_field(
                    name='Track info:',
                    value=f'''
                    `Time:` {utils.format_seconds(seconds=round(self.position) // 1000)} / {utils.format_seconds(seconds=round(self.current.length) // 1000)}
                    `Author:` {self.current.author}
                    `Source:` {self.current.source.value.title()}
                    '''
            )

        await self.send(embed=embed)

    async def send(self, *args, **kwargs) -> None:

        if not self.text_channel:
            return

        await self.text_channel.send(*args, **kwargs)

    #

    async def search(self, query: str, ctx: context.Context, source: slate.Source) -> Optional[slate.SearchResult]:

        try:
            search = await self.node.search(search=query, ctx=ctx, source=source)

        except (slate.HTTPError, obsidian.ObsidianSearchError):
            raise exceptions.EmbedError(embed=discord.Embed(colour=config.MAIN, description=f'{emoji.CROSS}  There was an error while searching for results.'))

        except slate.NoMatchesFound as error:
            raise exceptions.EmbedError(
                    embed=discord.Embed(
                            colour=config.MAIN,
                            description=f'{emoji.UNKNOWN}  No {error.source.value.lower().replace("_", " ")} {error.search_type.value}s were found for your query.'
                    )
            )

        if search.source in [slate.Source.HTTP, slate.Source.LOCAL] and ctx.author.id not in config.OWNER_IDS:
            raise exceptions.EmbedError(embed=discord.Embed(colour=config.MAIN, description=f'{emoji.CROSS}  You do not have permission to play tracks from `HTTP` or `LOCAL` sources.'))

        return search

    async def queue_search(self, query: str, ctx: context.Context, source: slate.Source, now: bool = False, next: bool = False) -> None:

        search = await self.search(query=query, ctx=ctx, source=source)

        self.queue.put(
                items=search.tracks[0] if search.type is slate.SearchType.TRACK else search.tracks,
                position=0 if (now or next) else None
        )
        if now:
            await self.stop()

        if search.type is slate.SearchType.TRACK:
            description = f'Added the {search.source.value.lower()} track [{search.tracks[0].title}]({search.tracks[0].uri}) to the queue.'
        else:
            description = f'Added the {search.source.value.lower()} {search.type.name.lower()} [{search.result.name}]({search.result.url}) to the queue.'

        embed = discord.Embed(colour=config.MAIN description=description)
        await ctx.reply(embed=embed)
