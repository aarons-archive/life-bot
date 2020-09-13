"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio

import discord
import humanize
import ksoftapi
import spotify
from discord.ext import commands

from bot import Life
from cogs.voice.lavalink import client, objects
from cogs.voice.lavalink.exceptions import *
from utilities import context, exceptions


class Music(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.bot.lavalink = client.Client(bot=self.bot, session=self.bot.session)
        self.bot.spotify = spotify.Client(client_id=self.bot.config.spotify_app_id, client_secret=self.bot.config.spotify_secret)
        self.bot.spotify_http = spotify.HTTPClient(client_id=self.bot.config.spotify_app_id, client_secret=self.bot.config.spotify_secret)
        self.bot.ksoft = ksoftapi.Client(self.bot.config.ksoft_token)

        self.load_task = asyncio.create_task(self.load())

    async def load(self) -> None:

        for node in self.bot.config.nodes:
            try:
                await self.bot.lavalink.create_node(host=node['host'], port=node['port'], password=node['password'], identifier=node['identifier'])
            except NodeCreationError as e:
                print(f'[LAVALINK] {e}')
            else:
                print(f'[LAVALINK] Node {node["identifier"]} connected.')

    @commands.Cog.listener()
    async def on_lavalink_track_start(self, event: objects.TrackStartEvent) -> None:

        await event.player.invoke_controller()

        event.player.wait_track_start.set()
        event.player.wait_track_start.clear()

    @commands.Cog.listener()
    async def on_lavalink_track_end(self, event: objects.TrackEndEvent) -> None:

        event.player.skip_requests.clear()

        event.player.wait_track_end.set()
        event.player.wait_track_end.clear()

    @commands.Cog.listener()
    async def on_lavalink_track_exception(self, event: objects.TrackExceptionEvent) -> None:

        await event.player.send(message=f'Something went wrong while playing the track `{event.track.title}`. Error: `{event.error}`')
        event.player.skip_requests.clear()

        event.player.wait_track_end.set()
        event.player.wait_track_end.clear()

    @commands.Cog.listener()
    async def on_lavalink_track_stuck(self, event: objects.TrackStuckEvent) -> None:

        await event.player.send(message=f'Something went wrong while playing the track `{event.track.title}`. Use `{self.bot.config.prefix}support` for more help.')
        event.player.skip_requests.clear()

        event.player.wait_track_end.set()
        event.player.wait_track_end.clear()

    @commands.Cog.listener()
    async def on_lavalink_websocket_closed(self, event: objects.WebSocketClosedEvent) -> None:

        if event.code == 1000:
            return

        await event.player.send(message=f'Your nodes websocket has disconnected. Use `{self.bot.config.prefix}support` for more help.')

        await event.player.destroy()
        event.player.task.cancel()

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx: context.Context) -> None:
        """
        Joins your voice channel.
        """

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel:
            raise exceptions.VoiceError('You must be in a voice channel to use this command.')

        if ctx.guild.voice_client and ctx.guild.voice_client.is_connected:

            if channel.id != ctx.guild.voice_client.channel.id:
                raise exceptions.VoiceError(f'I am already in the voice channel `{ctx.guild.voice_client.channel}`.')

            raise exceptions.VoiceError('I am already in your voice channel.')

        await self.bot.lavalink.connect(channel=channel)
        ctx.guild.voice_client.text_channel = ctx.channel
        await ctx.send(f'Joined your voice channel `{channel}`.')

    @commands.command(name='play')
    async def play(self, ctx: context.Context, *, query: str) -> None:
        """
        Plays or queues a track with the given search.

        `query`: The search term to find tracks for. You can prepend this query with soundcloud to search for soundcloud tracks.

        This command supports youtube/soundcloud searching or youtube, soundcloud, spotify, bandcamp, and vimeo links.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            await ctx.invoke(self.join)

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        async with ctx.channel.typing():

            search = await ctx.guild.voice_client.node.search(query=query, ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in self.bot.config.owner_ids:
                raise exceptions.VoiceError('You are unable to play HTTP links.')

            if search.source == 'spotify':

                if search.source_type == 'track':
                    message = f'Added the spotify track **{search.result.name}** to the queue.'
                elif search.source_type in ('album', 'playlist'):
                    message = f'Added the spotify {search.source_type} **{search.result.name}** to the queue with a total of **{len(search.tracks)}** track(s).'
                tracks = search.tracks

            else:

                if search.source_type == 'track':
                    message = f'Added the {search.source} track **{search.tracks[0].title}** to the queue.'
                    tracks = [search.tracks[0]]

                elif search.source_type == 'playlist':
                    message = f'Added the {search.source} playlist **{search.result.name}** to the queue with a total of **{len(search.tracks)}** track(s)'
                    tracks = search.tracks

            ctx.guild.voice_client.queue.put(tracks=tracks)
            await ctx.send(message)

    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    async def leave(self, ctx: context.Context) -> None:
        """
        Leaves the voice channel.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        await ctx.send(f'Left the voice channel `{ctx.voice_client.channel}`.')
        await ctx.guild.voice_client.destroy()

    @commands.command(name='skip', aliases=['stop'])
    async def skip(self, ctx: context.Context, amount: int = 1) -> None:
        """
        Skips an amount of tracks.

        `amount`: The amount of tracks to skip. Defaults to 1
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not ctx.guild.voice_client.is_playing:
            raise exceptions.VoiceError(f'There are no tracks playing.')

        if not ctx.guild.voice_client.current.requester.id == ctx.author.id:
            amount = 1

            if ctx.author not in ctx.guild.voice_client.listeners:
                raise exceptions.VoiceError('You can not vote to skip as your are currently deafened.')

            if ctx.author.id in ctx.guild.voice_client.skip_requests:

                ctx.guild.voice_client.skip_requests.remove(ctx.author.id)
                raise exceptions.VoiceError(f'Removed your vote to skip.')
            else:
                ctx.guild.voice_client.skip_requests.append(ctx.author.id)
                await ctx.send('Added your vote to skip.')

            skips_needed = (len(ctx.guild.voice_client.listeners) // 2) + 1
            if len(ctx.guild.voice_client.skip_requests) < skips_needed:
                raise exceptions.VoiceError(f'Currently on `{len(ctx.guild.voice_client.skip_requests)}` out of `{skips_needed}` votes needed to skip.')

        if not amount == 1:

            if amount <= 0 or amount > len(ctx.guild.voice_client.queue) + 1:
                raise exceptions.VoiceError(f'There are not enough tracks in the queue to skip that many. Choose a number between `1` and '
                                            f'`{len(ctx.guild.voice_client.queue) + 1}`.')

            for index, track in enumerate(ctx.guild.voice_client.queue[:amount - 1]):
                if not track.requester.id == ctx.author.id:
                    raise exceptions.VoiceError(f'You only skipped `{index + 1}` out of the next `{amount}` tracks because you were not the requester of all them.')

                await ctx.guild.voice_client.queue.get()

        await ctx.guild.voice_client.stop()
        await ctx.send(f'Skipped `{amount}` {"track." if amount == 1 else "tracks."}')
        return

    @commands.command(name='pause')
    async def pause(self, ctx: context.Context) -> None:
        """
        Pauses the player.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.is_paused:
            raise exceptions.VoiceError('The player is already paused.')

        await ctx.guild.voice_client.set_pause(pause=True)
        await ctx.send(f'The player is now paused.')

    @commands.command(name='unpause', aliases=['resume'])
    async def unpause(self, ctx: context.Context) -> None:
        """
        Resumes the player.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.paused is False:
            raise exceptions.VoiceError('The player is not paused.')

        await ctx.guild.voice_client.set_pause(pause=False)
        await ctx.send(f'The player is now un-paused')

    @commands.command(name='seek')
    async def seek(self, ctx: context.Context, seconds: int = None) -> None:
        """
        Changes the position of the player.

        `position`: The position to seek too, in seconds.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not ctx.guild.voice_client.is_playing:
            raise exceptions.VoiceError(f'There are no tracks playing.')

        if not ctx.guild.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        if not seconds and not seconds == 0:
            await ctx.send(f'The players position is `{self.bot.utils.format_seconds(seconds=ctx.guild.voice_client.position / 1000)}`')
            return

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.guild.voice_client.current.length:
            raise exceptions.VoiceError(f'That was not a valid position. Please choose a value between `0` and `{round(ctx.guild.voice_client.current.length / 1000)}`.')

        await ctx.guild.voice_client.set_position(position=milliseconds)
        await ctx.send(f'The players position is now `{self.bot.utils.format_seconds(seconds=milliseconds / 1000)}`.')

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx: context.Context, volume: int = None) -> None:
        """
        Changes the volume of the player.

        `volume`: The volume to change too, between 0 and 100.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not volume and not volume == 0:
            await ctx.send(f'The players volume is `{ctx.guild.voice_client.volume}%`.')
            return

        if volume < 0 or volume > 100:
            raise exceptions.VoiceError(f'That was not a valid volume, Please choose a value between `0` and and `100`.')

        await ctx.guild.voice_client.set_volume(volume=volume)
        await ctx.send(f'The players volume is now `{ctx.guild.voice_client.volume}%`.')

    @commands.command(name='now_playing', aliases=['np'])
    async def now_playing(self, ctx: context.Context) -> None:
        """
        Displays the player controller.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        if not ctx.guild.voice_client.is_playing:
            raise exceptions.VoiceError(f'There are no tracks playing.')

        await ctx.guild.voice_client.invoke_controller()

    @commands.group(name='queue', aliases=['q'], invoke_without_command=True)
    async def queue(self, ctx: context.Context) -> None:
        """
        Displays the queue.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')
        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        time = self.bot.utils.format_seconds(seconds=round(sum([track.length for track in ctx.guild.voice_client.queue])) / 1000, friendly=True)
        header = f'Showing `{min([10, len(ctx.guild.voice_client.queue)])}` out of `{len(ctx.guild.voice_client.queue)}` track(s) in the queue. ' \
                 f'Total queue time is `{time}`.\n\n'

        entries = []
        for index, track in enumerate(ctx.guild.voice_client.queue):
            entries.append(f'**{index + 1}.** [{str(track.title)}]({track.uri}) | `{self.bot.utils.format_seconds(seconds=round(track.length) / 1000)}` | '
                           f'{track.requester.mention}')

        await ctx.paginate_embed(entries=entries, per_page=10, title='Queue:', header=header)

    @queue.command(name='clear')
    async def queue_clear(self, ctx: context.Context) -> None:
        """
        Clears the queue.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.guild.voice_client.queue.clear()
        await ctx.send(f'The queue has been cleared.')

    @queue.command(name='detailed', aliases=['detail', 'd'])
    async def queue_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queue.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')
        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        entries = []
        for index, track in enumerate(ctx.guild.voice_client.queue):
            embed = discord.Embed(colour=ctx.colour)
            embed.set_image(url=track.thumbnail)
            embed.description = f'Showing detailed information about track `{index + 1}` out of `{len(ctx.guild.voice_client.queue)}` in the queue.\n\n' \
                                f'[{track.title}]({track.uri})\n\nAuthor: `{track.author}`\nSource: `{track.source}`\n' \
                                f'Length: `{self.bot.utils.format_seconds(seconds=round(track.length) / 1000, friendly=True)}`\n' \
                                f'Is seekable: `{track.is_seekable}`\nIs stream: `{track.is_stream}`\nRequester: {track.requester.mention}'
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue.group(name='history', aliases=['h'], invoke_without_command=True)
    async def queue_history(self, ctx: context.Context) -> None:
        """
        Displays the queue history.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        history = list(ctx.guild.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        time = self.bot.utils.format_seconds(seconds=round(sum([track.length for track in history])) / 1000, friendly=True)
        header = f'Showing `{min([10, len(history)])}` out of `{len(history)}` track(s) in the queues history. Total queue history time is `{time}`.\n\n'

        entries = []
        for index, track in enumerate(history):
            entries.append(f'**{index + 1}.** [{str(track.title)}]({track.uri}) | `{self.bot.utils.format_seconds(seconds=round(track.length) / 1000)}` | '
                           f'{track.requester.mention}')

        await ctx.paginate_embed(entries=entries, per_page=10, title='Queue history:', header=header)

    @queue_history.command(name='clear')
    async def queue_history_clear(self, ctx: context.Context) -> None:
        """
        Clears the queue history.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        history = list(ctx.guild.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        ctx.guild.voice_client.queue.clear_history()
        await ctx.send(f'The queue history has been cleared.')

    @queue_history.command(name='detailed', aliases=['detail', 'd'])
    async def queue_history_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queues history.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        history = list(ctx.guild.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        entries = []
        for index, track in enumerate(history):
            embed = discord.Embed(colour=ctx.colour)
            embed.set_image(url=track.thumbnail)
            embed.description = f'Showing detailed information about track `{index + 1}` out of `{len(history)}` in the queue history.\n\n' \
                                f'[{track.title}]({track.uri})\n\nAuthor: `{track.author}`\nSource: `{track.source}`\n' \
                                f'Length: `{self.bot.utils.format_seconds(seconds=round(track.length) / 1000, friendly=True)}`\n' \
                                f'Is seekable: `{track.is_seekable}`\nIs stream: `{track.is_stream}`\nRequester: {track.requester.mention}'
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue.command(name='shuffle')
    async def queue_shuffle(self, ctx: context.Context) -> None:
        """
        Shuffles the queue.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.guild.voice_client.queue.shuffle()
        await ctx.send(f'The queue has been shuffled.')

    @queue.command(name='reverse')
    async def queue_reverse(self, ctx: context.Context) -> None:
        """
        Reverses the queue.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.guild.voice_client.queue.reverse()
        await ctx.send(f'The queue has been reversed.')

    @queue.command(name='sort')
    async def queue_sort(self, ctx: context.Context, method: str, reverse: bool = False) -> None:
        """
        Sorts the queue.

        `method`: The method to sort the queue with. Can be `title`, `author` or `length`.
        `reverse`: Whether or not to reverse the sort, as in `5, 3, 2, 4, 1` -> `5, 4, 3, 2, 1` instead of `5, 3, 2, 4, 1` -> `1, 2, 3, 4, 5`.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        ctx.guild.voice_client.queue.sort(method=method, reverse=reverse)
        await ctx.send(f'The queue has been sorted with method `{method}`.')

    @queue.command(name='remove')
    async def queue_remove(self, ctx: context.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        `entry`: The position of the track you want to remove.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')

        if entry <= 0 or entry > len(ctx.guild.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry. Choose a number between `1` and `{len(ctx.guild.voice_client.queue)}` ')

        item = await ctx.guild.voice_client.queue.get(position=entry - 1, history=False)
        await ctx.send(f'Removed `{item.title}` from the queue.')

    @queue.command(name='move')
    async def queue_move(self, ctx: context.Context, entry_1: int = 0, entry_2: int = 0) -> None:
        """
        Move a track in the queue to a different position.

        `entry_1`: The position of the track you want to move from.
        `entry_2`: The position of the track you want to move too.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The players queue is empty.')


        if entry_1 <= 0 or entry_1 > len(ctx.guild.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry to move from. Choose a number between `1` and `{len(ctx.guild.voice_client.queue)}` ')

        if entry_2 <= 0 or entry_2 > len(ctx.guild.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry to move too. Choose a number between `1` and `{len(ctx.guild.voice_client.queue)}` ')

        track = await ctx.guild.voice_client.queue.get(position=entry_1 - 1, history=False)
        ctx.guild.voice_client.queue.put(tracks=track, position=entry_2 - 1)
        await ctx.send(f'Moved `{track.title}` from position `{entry_1}` to position `{entry_2}`.')

    @queue.command(name='loop')
    async def queue_loop(self, ctx: context.Context) -> None:
        """
        Loops the queue.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            raise exceptions.VoiceError('I am not connected to any voice channels.')

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.guild.voice_client.queue.is_looping is True:
            ctx.guild.voice_client.queue.looping = False
            await ctx.send(f'The queue will stop looping.')
        else:
            ctx.guild.voice_client.queue.looping = True
            await ctx.send(f'The queue will start looping.')

    @commands.command(name='lavalink', aliases=['ll'])
    async def lavalink(self, ctx: context.Context) -> None:
        """
        Display stats about the bots lavalink connection.
        """

        embed = discord.Embed(colour=ctx.colour)
        embed.add_field(name='Lavalink stats:', value=f'`Players:` {len(self.bot.lavalink.players)}\n`Nodes:` {len(self.bot.lavalink.nodes)}', inline=False)

        for node in self.bot.lavalink.nodes.values():

            active_players = len([player for player in node.players.values() if player.is_connected])
            uptime = self.bot.utils.format_seconds(seconds=round(node.stats.uptime / 1000), friendly=True)
            reservable = humanize.naturalsize(node.stats.memory_reservable)
            allocated = humanize.naturalsize(node.stats.memory_allocated)
            used = humanize.naturalsize(node.stats.memory_used)
            free = humanize.naturalsize(node.stats.memory_free)
            cpu_cores = node.stats.cpu_cores

            embed.add_field(name=f'Node: {node.identifier}', value=f'`Players:` {len(node.players)}\n`Active players:` {active_players}\n'
                                                                   f'`Memory reservable:` {reservable}\n`Memory allocated:` {allocated}\n'
                                                                   f'`Memory used:` {used}\n`Memory free:` {free}\n`CPU Cores:` {cpu_cores}\n`Uptime:` {uptime}')

        await ctx.send(embed=embed)

    @commands.command(nane='lyrics', aliases=['lyric'])
    async def lyrics(self, ctx: context.Context, *, query: str = None) -> None:

        if query is None:
            if not ctx.guild or not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
                raise exceptions.VoiceError('I am not connected to any voice channels.')
            if not ctx.guild.voice_client.is_playing:
                raise exceptions.VoiceError(f'There are no tracks playing.')
            query = f'{ctx.guild.voice_client.current.title} - {ctx.guild.voice_client.current.requester}'

        try:
            results = await self.bot.ksoft.music.lyrics(query=query, limit=20)
        except ksoftapi.NoResults:
            raise exceptions.ArgumentError(f'No lyrics were found for the query `{query}`.')
        except ksoftapi.APIError:
            raise exceptions.VoiceError('Lyric API is currently down.')

        paginator = await ctx.paginate_embed(entries=[f'`{index + 1}.` {result.name} - {result.artist}' for index, result in enumerate(results)], per_page=10,
                                             header='Please choose the number of the track you would like lyrics for:\n')

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            raise exceptions.ArgumentError('You took too long to respond.')

        response = await self.bot.clean_content.convert(ctx, response.content)
        try:
            response = int(response) - 1
        except ValueError:
            raise exceptions.ArgumentError('That was not a valid number.')
        if response < 0 or response >= len(results):
            raise exceptions.ArgumentError('That was not one of the available tracks.')

        await paginator.stop()

        result = results[response]

        entries = []
        for line in result.lyrics.split('\n'):

            if len(entries) == 0:
                entries.append(line)
                continue

            last_entry = entries[len(entries) - 1]
            if len(last_entry) >= 1000 or len(last_entry) + len(line) >= 1000:
                entries.append(line)
                continue

            entries[len(entries) - 1] += f'\n{line}'

        await ctx.paginate_embed(entries=entries, header=f'Lyrics for `{result.name}` by `{result.artist}`:\n\n',
                                 embed_add_footer='Lyrics provided by KSoft.Si API', per_page=1)


def setup(bot):
    bot.add_cog(Music(bot))
