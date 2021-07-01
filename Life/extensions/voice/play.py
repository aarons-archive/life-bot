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

from typing import Union

import discord
import slate
from discord.ext import commands

from core import colours
from core.bot import Life
from utilities import checks, context


class Options(commands.FlagConverter, delimiter=' ', prefix='--', case_insensitive=True):
    music: bool = False
    soundcloud: bool = False
    local: bool = False
    http: bool = False
    next: bool = False
    now: bool = False


class QueueOptions(commands.FlagConverter, delimiter=' ', prefix='--', case_insensitive=True):
    next: bool = False
    now: bool = False


class SearchOptions(commands.FlagConverter, delimiter=' ', prefix='--', case_insensitive=True):
    music: bool = False
    soundcloud: bool = False
    local: bool = False
    http: bool = False


def get_source(flags: Union[Options, SearchOptions]) -> slate.Source:

    if flags.music:
        return slate.Source.YOUTUBE_MUSIC
    elif flags.soundcloud:
        return slate.Source.SOUNDCLOUD
    elif flags.local:
        return slate.Source.LOCAL
    elif flags.http:
        return slate.Source.HTTP

    return slate.Source.YOUTUBE


class Play(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name='play', invoke_without_command=True)
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play(self, ctx: context.Context, query: str, *, options: Options) -> None:
        """
        Queues tracks with the given name or url.

        `query`: The query to search for tracks with.

        **Flags:**
        `--music`: Searches [youtube music](https://music.youtube.com/) for results. This is useful for playing non-music video tracks.
        `--soundcloud`: Searches [soundcloud](https://soundcloud.com/) for results.
        `--next`: Places the track that is found at the start of the queue.
        `--now`: Skips the current track and plays the track that is found.

        **Usage:**
        `l-play If I Can't Have You by Shawn Mendes --now`
        `l-play Senorita by Shawn Mendes --next`
        `l-play Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=get_source(options))

    #

    @commands.command(name='yt-music', aliases=['yt_music', 'ytmusic', 'youtube-music', 'youtube_music', 'youtubemusic', 'ytm'])
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def yt_music(self, ctx: context.Context, query: str, *, options: QueueOptions) -> None:
        """
        Queues tracks from youtube music with the given name or url.

        `query`: The query to search for tracks with.

        **Flags:**
        `--next`: Places the track that is found at the start of the queue.
        `--now`: Skips the current track and plays the track that is found.

        **Usage:**
        `l-yt-music Lost In Japan by Shawn Mendes --now`
        `l-ytm If I Can't Have You by Shawn Mendes --next`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.YOUTUBE_MUSIC)

    @commands.command(name='soundcloud', aliases=['sc'])
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def soundcloud(self, ctx: context.Context, query: str, *, options: QueueOptions) -> None:
        """
        Queues tracks from soundcloud with the given name or url.

        `query`: The query to search for tracks with.

        **Flags:**
        `--next`: Places the track that is found at the start of the queue.
        `--now`: Skips the current track and plays the track that is found.

        **Usage:**
        `l-soundcloud Lost In Japan by Shawn Mendes --now`
        `l-sc If I Can't Have You by Shawn Mendes --next`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=options.now, next=options.next, source=slate.Source.SOUNDCLOUD)

    #

    @commands.command(name='play-next', aliases=['play_next', 'playnext', 'pnext'])
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play_next(self, ctx: context.Context, query: str, *, options: SearchOptions) -> None:
        """
        Queues tracks at the start of the queue.

        `query`: The query to search for tracks with.

        **Flags:**
        `--music`: Searches [youtube music](https://music.youtube.com/) for results. This is useful for playing non-music video tracks.
        `--soundcloud`: Searches [soundcloud](https://soundcloud.com/) for results.

        **Usage:**
        `l-play-next Lost In Japan by Shawn Mendes --music`
        `l-pnext If I Can't Have You by Shawn Mendes --soundcloud`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, next=True, source=get_source(options))

    @commands.command(name='play-now', aliases=['play_now', 'playnow', 'pnow'])
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def play_now(self, ctx: context.Context, query: str, *, options: SearchOptions) -> None:
        """
        Queues tracks and skips the current track.

        `query`: The query to search for tracks with.

        **Flags:**
        `--music`: Searches [youtube music](https://music.youtube.com/) for results. This is useful for playing non-music video tracks.
        `--soundcloud`: Searches [soundcloud](https://soundcloud.com/) for results.

        **Usage:**
        `l-play-now Lost In Japan by Shawn Mendes --music`
        `l-pnow If I Can't Have You by Shawn Mendes --soundcloud`
        """

        async with ctx.channel.typing():
            await ctx.voice_client.queue_search(query=query, ctx=ctx, now=True, source=get_source(options))

    #

    @commands.command(name='search')
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client(try_join=True)
    async def search(self, ctx: context.Context, query: str, *, options: Options) -> None:
        """
        Allows you to choose which track to play based on a search.

        `query`: The query to search for tracks with.

        **Flags:**
        `--music`: Searches [youtube music](https://music.youtube.com/) for results. This is useful for playing non-music video tracks.
        `--soundcloud`: Searches [soundcloud](https://soundcloud.com/) for results.
        `--next`: Places the track that is chosen at the start of the queue.
        `--now`: Skips the current track and plays the track that is chosen.

        **Usage:**
        `l-search If I Can't Have You by Shawn Mendes --now`
        `l-search Senorita by Shawn Mendes --next`
        `l-search Lost In Japan by Shawn Mendes --soundcloud --now`
        """

        search = await ctx.voice_client.search(query=query, ctx=ctx, source=get_source(options))

        if search.type in {slate.SearchType.TRACK, slate.SearchType.ARTIST}:
            choice = await ctx.choice(entries=[f'`{index + 1}.` [{track.title}]({track.uri})' for index, track in enumerate(search.tracks)], per_page=10, title=f'Search results for `{query}`:')
            tracks = search.tracks[choice[0]]
        else:
            tracks = search.tracks

        ctx.voice_client.queue.put(
                items=tracks,
                position=0 if (options.now or options.next) else None
        )
        if options.now:
            await ctx.voice_client.stop()

        if search.type is slate.SearchType.TRACK:
            description = f'Added the {search.source.value.lower()} track [{search.tracks[0].title}]({search.tracks[0].uri}) to the queue.'
        else:
            description = f'Added the {search.source.value.lower()} {search.type.name.lower()} [{search.result.name}]({search.result.url}) to the queue.'

        embed = discord.Embed(colour=colours.MAIN, description=description)
        await ctx.reply(embed=embed)


def setup(bot: Life) -> None:
    bot.add_cog(Play(bot=bot))
