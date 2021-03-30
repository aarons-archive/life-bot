#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
#

from typing import Literal

import discord
import ksoftapi
from discord.ext import commands

import config
import slate
from bot import Life
from cogs.voice.custom.player import Player
from utilities import context, exceptions, utils


class Music(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    async def load(self) -> None:

        for node in config.NODES:
            try:
                await self.bot.slate.create_node(cls=getattr(slate, node.pop('type')), **node)
            except (slate.NodeConnectionError, slate.NodeCreationError) as e:
                print(f'[SLATE] {e}')
            else:
                print(f'[SLATE] Node \'{node["identifier"]}\' connected.')

    #

    @commands.Cog.listener()
    async def on_slate_track_start(self, event: slate.TrackStartEvent) -> None:

        event.player.track_start_event.set()
        event.player.track_start_event.clear()

        await event.player.invoke_controller()

    @commands.Cog.listener()
    async def on_slate_track_end(self, event: slate.TrackEndEvent) -> None:

        event.player.track_end_event.set()
        event.player.track_end_event.clear()

        event.player.skip_request_ids.clear()

    @commands.Cog.listener()
    async def on_slate_track_exception(self, event: slate.TrackExceptionEvent) -> None:

        track = None
        try:
            track = await event.player.node.decode_tracks(track_id=event.track, retry=False)
        except slate.HTTPError:
            pass

        title = getattr(track or event.player.current, 'title', 'Not Found')
        await event.player.send(f'There was an error of severity `{event.severity}` while playing the track `{title}`.\nReason: {event.message}')

        event.player.track_end_event.set()
        event.player.track_end_event.clear()

        event.player.skip_request_ids.clear()

    @commands.Cog.listener()
    async def on_slate_track_stuck(self, event: slate.TrackStuckEvent) -> None:

        track = None
        try:
            track = await event.player.node.decode_tracks(track_id=event.track, retry=False)
        except slate.HTTPError:
            pass

        title = getattr(track or event.player.current, 'title', 'Not Found')
        await event.player.send(f'Something went wrong while playing the track `{title}`. Use `{config.PREFIX}support` for more help.')

        event.player.track_end_event.set()
        event.player.track_end_event.clear()

        event.player.skip_request_ids.clear()

    #

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx: context.Context) -> None:
        """
        Joins your voice channel.
        """

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel:
            raise exceptions.VoiceError('You must be in a voice channel to use this command.')

        if ctx.voice_client and ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am already in a voice channel.')

        if ctx.voice_client:
            await ctx.voice_client.reconnect(channel=channel)
        else:
            await self.bot.slate.create_player(channel=channel, cls=Player)

        ctx.voice_client.text_channel = ctx.channel
        await ctx.send(f'Joined the voice channel `{channel}`.')

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx: context.Context, *, query: str) -> None:
        """
        Plays or queues a track with the given search.

        `query`: The search term to find tracks for. You can prepend this query with soundcloud to search for tracks on soundcloud.

        This command supports youtube/soundcloud searching or youtube, soundcloud, spotify, bandcamp, beam, twitch, and vimeo links.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            await ctx.invoke(self.join)

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        async with ctx.channel.typing():

            search = await ctx.voice_client.search(query=query, ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in config.OWNER_IDS:
                raise exceptions.VoiceError('You are unable to play HTTP links.')

            if search.source == 'spotify':

                message = f'Added the Spotify {search.search_type} `{search.search_result.name}` to the queue.'
                if search.search_type in ('album', 'playlist'):
                    message = f'{message[:-1]} with a total of `{len(search.tracks)}` tracks.'

                tracks = search.tracks

            else:

                if search.search_type == 'track':
                    message = f'Added the {search.source} {search.search_type} `{search.tracks[0].title}` to the queue.'
                    tracks = [search.tracks[0]]
                elif search.search_type == 'playlist':
                    message = f'Added the {search.source} {search.search_type} `{search.search_result.name}` to the queue with a total of **{len(search.tracks)}** track(s)'
                    tracks = search.tracks

            ctx.voice_client.queue.put(items=tracks)
            await ctx.send(message)

    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    async def leave(self, ctx: context.Context) -> None:
        """
        Leaves the voice channel.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        await ctx.send(f'Left the voice channel `{ctx.voice_client.channel}`.')
        await ctx.voice_client.stop()
        await ctx.voice_client.disconnect()

    @commands.command(name='destroy')
    async def destroy(self, ctx: context.Context) -> None:
        """
        Completely destroys the guilds player.
        """

        if not ctx.voice_client:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        await ctx.send(f'Destroyed this guilds player.')
        await ctx.voice_client.destroy()

    @commands.command(name='skip', aliases=['stop', 'next'])
    async def skip(self, ctx: context.Context, amount: int = 1) -> None:
        """
        Skips an amount of tracks.

        `amount`: The amount of tracks to skip. Defaults to 1
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not ctx.voice_client.is_playing:
            raise exceptions.VoiceError(f'There are no tracks playing.')

        if ctx.voice_client.current.requester.id != ctx.author.id and ctx.author.id not in config.OWNER_IDS:
            amount = 1

            if ctx.author not in ctx.voice_client.listeners:
                raise exceptions.VoiceError('You can not vote to skip as you are currently deafened or server deafened.')

            if ctx.author.id in ctx.voice_client.skip_request_ids:
                ctx.voice_client.skip_request_ids.remove(ctx.author.id)
                raise exceptions.VoiceError(f'Removed your vote to skip.')
            else:
                ctx.voice_client.skip_request_ids.append(ctx.author.id)
                await ctx.send('Added your vote to skip.')

            skips_needed = (len(ctx.voice_client.listeners) // 2) + 1
            if len(ctx.voice_client.skip_request_ids) < skips_needed:
                raise exceptions.VoiceError(f'Currently on `{len(ctx.voice_client.skip_request_ids)}` out of `{skips_needed}` votes needed to skip.')

        if amount != 1:

            if amount <= 0 or amount > len(ctx.voice_client.queue) + 1:
                raise exceptions.VoiceError(f'There are not enough tracks in the queue to skip that many. Choose a number between `1` and `{len(ctx.voice_client.queue) + 1}`.')

            for index, track in enumerate(ctx.voice_client.queue[:amount - 1]):
                if track.requester.id != ctx.author.id:
                    raise exceptions.VoiceError(f'You only skipped `{index + 1}` out of the next `{amount}` tracks because you were not the requester of all them.')

                ctx.voice_client.queue.get()

        await ctx.voice_client.stop()
        await ctx.send(f'Skipped `{amount}` {"track." if amount == 1 else "tracks."}')

    @commands.command(name='pause')
    async def pause(self, ctx: context.Context) -> None:
        """
        Pauses the player.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.is_paused:
            raise exceptions.VoiceError('The player is already paused.')

        await ctx.voice_client.set_pause(pause=True)
        await ctx.send(f'The player is now paused.')

    @commands.command(name='unpause', aliases=['resume'])
    async def unpause(self, ctx: context.Context) -> None:
        """
        Resumes the player.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.is_paused is False:
            raise exceptions.VoiceError('The player is not paused.')

        await ctx.voice_client.set_pause(pause=False)
        await ctx.send(f'The player is now resumed.')

    @commands.command(name='seek')
    async def seek(self, ctx: context.Context, seconds: int = None) -> None:
        """
        Changes the position of the player.

        `position`: The position to seek too, in seconds.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not ctx.voice_client.is_playing:
            raise exceptions.VoiceError(f'There are no tracks playing.')

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        if not seconds and seconds != 0:
            await ctx.send(f'The players position is `{utils.format_seconds(seconds=ctx.voice_client.position / 1000)}`')
            return

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.voice_client.current.length:
            raise exceptions.VoiceError(f'That was not a valid position. Please choose a value between `0` and `{round(ctx.voice_client.current.length / 1000)}`.')

        await ctx.voice_client.set_position(position=milliseconds)
        await ctx.send(f'The players position is now `{utils.format_seconds(seconds=milliseconds // 1000)}`.')

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx: context.Context, volume: int = None) -> None:
        """
        Changes the volume of the player.

        `volume`: The volume to change too, between 0 and 100.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not volume and volume != 0:
            await ctx.send(f'The players volume is `{ctx.voice_client.volume}%`.')
            return

        if volume < 0 or volume > 100 and ctx.author.id not in config.OWNER_IDS:
            raise exceptions.VoiceError(f'That was not a valid volume, Please choose a value between `0` and and `100`.')

        await ctx.voice_client.set_volume(volume=volume)
        await ctx.send(f'The players volume is now `{ctx.voice_client.volume}%`.')

    @commands.command(name='now_playing', aliases=['np'])
    async def now_playing(self, ctx: context.Context) -> None:
        """
        Displays the player controller.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        if not ctx.voice_client.is_playing:
            raise exceptions.VoiceError(f'There are no tracks playing.')

        await ctx.voice_client.invoke_controller()

    @commands.group(name='queue', aliases=['q'], invoke_without_command=True)
    async def queue(self, ctx: context.Context) -> None:
        """
        Displays the queue.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')
        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        time = utils.format_seconds(seconds=round(sum(track.length for track in ctx.voice_client.queue)) // 1000, friendly=True)
        header = f'Showing `{min([10, len(ctx.voice_client.queue)])}` out of `{len(ctx.voice_client.queue)}` track(s) in the queue. Total queue time is `{time}`.\n\n'

        entries = [
            f'`{index + 1}.` [{str(track.title)}]({track.uri}) | {utils.format_seconds(seconds=round(track.length) // 1000)} | {track.requester.mention}'
            for index, track in enumerate(ctx.voice_client.queue)
        ]

        await ctx.paginate_embed(entries=entries, per_page=10, title='Queue:', header=header)

    @queue.command(name='detailed', aliases=['d'])
    async def queue_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queue.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')
        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        entries = []
        for index, track in enumerate(ctx.voice_client.queue):
            embed = discord.Embed(colour=ctx.colour)
            embed.set_image(url=track.thumbnail)
            embed.description = f'Showing detailed information about track `{index + 1}` out of `{len(ctx.voice_client.queue)}` in the queue.\n\n' \
                                f'[{track.title}]({track.uri})\n\n`Author:` {track.author}\n`Source:` {track.source}\n' \
                                f'`Length:` {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}\n' \
                                f'`Live:` {track.is_stream}\n`Seekable:` {track.is_seekable}\n`Requester:` {track.requester.mention}'
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue.command(name='clear', aliases=['c'])
    async def queue_clear(self, ctx: context.Context) -> None:
        """
        Clears the queue.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.voice_client.queue.clear()
        await ctx.send(f'The queue has been cleared.')

    @queue.group(name='history', aliases=['h'], invoke_without_command=True)
    async def queue_history(self, ctx: context.Context) -> None:
        """
        Displays the queue history.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        history = list(ctx.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        time = utils.format_seconds(seconds=round(sum(track.length for track in history)) // 1000, friendly=True)
        header = f'Showing `{min([10, len(history)])}` out of `{len(history)}` track(s) in the queues history. Total queue history time is `{time}`.\n\n'

        entries = [
            f'`{index + 1}.` [{str(track.title)}]({track.uri}) | {utils.format_seconds(seconds=round(track.length) // 1000)} | {track.requester.mention}'
            for index, track in enumerate(history)
        ]

        await ctx.paginate_embed(entries=entries, per_page=10, title='Queue history:', header=header)

    @queue_history.command(name='detailed', aliases=['d'])
    async def queue_history_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queues history.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        history = list(ctx.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        entries = []
        for index, track in enumerate(history):
            embed = discord.Embed(colour=ctx.colour)
            embed.set_image(url=track.thumbnail)
            embed.description = f'Showing detailed information about track `{index + 1}` out of `{len(history)}` in the queue history.\n\n' \
                                f'[{track.title}]({track.uri})\n\n`Author:` {track.author}\n`Source:` {track.source}\n' \
                                f'`Length:` {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}\n' \
                                f'`Live:` {track.is_stream}\n`Seekable:` {track.is_seekable}\n`Requester:` {track.requester.mention}'
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue_history.command(name='clear', aliases=['c'])
    async def queue_history_clear(self, ctx: context.Context) -> None:
        """
        Clears the queue history.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        history = list(ctx.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        ctx.voice_client.queue.clear_history()
        await ctx.send(f'The queue history has been cleared.')

    @queue.command(name='shuffle')
    async def queue_shuffle(self, ctx: context.Context) -> None:
        """
        Shuffles the queue.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.voice_client.queue.shuffle()
        await ctx.send(f'The queue has been shuffled.')

    @queue.command(name='reverse')
    async def queue_reverse(self, ctx: context.Context) -> None:
        """
        Reverses the queue.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.voice_client.queue.reverse()
        await ctx.send(f'The queue has been reversed.')

    @queue.group(name='loop', aliases=['l'], invoke_without_command=True)
    async def queue_loop(self, ctx: context.Context) -> None:
        """
        Loops the whole queue.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        ctx.voice_client.queue.set_looping(looping=not ctx.voice_client.queue.is_looping, current=False)
        await ctx.send(f'I will {"start" if ctx.voice_client.queue.is_looping else "stop"} looping the whole queue.')

    @queue_loop.command(name='current', aliases=['c'])
    async def queue_loop_current(self, ctx: context.Context) -> None:
        """
        Loops the current track.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        ctx.voice_client.queue.set_looping(looping=not ctx.voice_client.queue.is_looping, current=True)
        await ctx.send(f'I will {"start" if ctx.voice_client.queue.is_looping else "stop"} looping the current track.')

    @queue.command(name='sort')
    async def queue_sort(self, ctx: context.Context, method: Literal['title', 'length', 'author'], reverse: bool = False) -> None:
        """
        Sorts the queue.

        `method`: The method to sort the queue with. Can be `title`, `length` or `author`.
        `reverse`: Whether or not to reverse the sort, as in `5, 3, 2, 4, 1` -> `5, 4, 3, 2, 1` instead of `5, 3, 2, 4, 1` -> `1, 2, 3, 4, 5`.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        if method == 'title':
            ctx.voice_client.queue._queue.sort(key=lambda track: track.title, reverse=reverse)
        elif method == 'author':
            ctx.voice_client.queue._queue.sort(key=lambda track: track.author, reverse=reverse)
        elif method == 'length':
            ctx.voice_client.queue._queue.sort(key=lambda track: track.length, reverse=reverse)

        await ctx.send(f'The queue has been sorted with method `{method}`.')

    @queue.command(name='remove')
    async def queue_remove(self, ctx: context.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        `entry`: The position of the track you want to remove.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry. Choose a number between `1` and `{len(ctx.voice_client.queue)}` ')

        item = ctx.voice_client.queue.get(position=entry - 1, put_history=False)
        await ctx.send(f'Removed `{item.title}` from the queue.')

    @queue.command(name='move')
    async def queue_move(self, ctx: context.Context, entry_1: int = 0, entry_2: int = 0) -> None:
        """
        Move a track in the queue to a different position.

        `entry_1`: The position of the track you want to move from.
        `entry_2`: The position of the track you want to move too.
        """

        if not ctx.voice_client or not ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        if entry_1 <= 0 or entry_1 > len(ctx.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry to move from. Choose a number between `1` and `{len(ctx.voice_client.queue)}` ')

        if entry_2 <= 0 or entry_2 > len(ctx.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry to move too. Choose a number between `1` and `{len(ctx.voice_client.queue)}` ')

        track = ctx.voice_client.queue.get(position=entry_1 - 1, put_history=False)
        ctx.voice_client.queue.put(items=track, position=entry_2 - 1)
        await ctx.send(f'Moved `{track.title}` from position `{entry_1}` to position `{entry_2}`.')

    @commands.command(name='lyrics')
    async def lyrics(self, ctx: context.Context, *, query: str = 'spotify') -> None:

        if query == 'spotify':

            query = 'player'
            if (spotify_activity := discord.utils.find(lambda activity: isinstance(activity, discord.Spotify), ctx.author.activities)) is not None:
                query = f'{spotify_activity.title} - {spotify_activity.album} - {spotify_activity.artist}'

        if query == 'player':

            if not ctx.voice_client or not ctx.voice_client.is_connected:
                raise exceptions.VoiceError('I am not connected to any voice channels.')
            if not ctx.voice_client.is_playing:
                raise exceptions.VoiceError(f'There are no tracks playing.')

            query = f'{ctx.voice_client.current.title} - {ctx.voice_client.current.requester}'

        try:
            results = await self.bot.ksoft.music.lyrics(query=query, limit=50)
        except ksoftapi.NoResults:
            raise exceptions.ArgumentError(f'No results were found for the query `{query}`.')
        except ksoftapi.APIError:
            raise exceptions.VoiceError('The API used to fetch lyrics is currently down/broken.')

        choice = await ctx.paginate_choice(entries=[f'`{index + 1}.` {result.name} - {result.artist}' for index, result in enumerate(results)], per_page=10,
                                           header=f'**__Please choose the number of the track you would like lyrics for:__**\n`Query`: {query}\n\n')
        result = results[choice]

        entries = []
        for line in result.lyrics.split('\n'):

            if not entries:
                entries.append(line)
                continue

            last_entry = entries[-1]
            if len(last_entry) >= 1000 or len(last_entry) + len(line) >= 1000:
                entries.append(line)
                continue

            entries[-1] += f'\n{line}'

        await ctx.paginate_embed(
                entries=entries, per_page=1, header=f'**Lyrics for `{result.name}` by `{result.artist}`:**\n\n', embed_add_footer='Lyrics provided by KSoft.Si API.'
        )


def setup(bot: Life):
    bot.add_cog(Music(bot))
