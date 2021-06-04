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
import slate
from discord.ext import commands

import config
from bot import Life
from cogs.voice.custom.player import Player
from utilities import context, exceptions, utils


def is_connected(same_channel: bool = False):

    async def predicate(ctx) -> bool:
        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel:
            message = 'You must be connected to a voice channel to use this command.'
            if same_channel and getattr(channel, 'id', None) != getattr(getattr(ctx.voice_client, 'channel', None), 'id', None):
                message = 'You must be connected to the same voice channel as me to use this command.'
            raise exceptions.VoiceError(message)
        return True

    return commands.check(predicate)


def has_voice_client(try_join: bool = False):

    async def predicate(ctx) -> bool:
        if not ctx.voice_client or not ctx.voice_client.is_connected:
            if try_join:
                await ctx.invoke(ctx.bot.get_command('join'))
            else:
                raise exceptions.VoiceError('I am not connected to any voice channels.')
        return True

    return commands.check(predicate)


def is_voice_client_playing():

    async def predicate(ctx) -> bool:
        if not ctx.voice_client or not ctx.voice_client.is_playing:
            raise exceptions.VoiceError('No tracks are currently playing.')
        return True

    return commands.check(predicate)


class Music(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    """
    async def load(self) -> None: 

        for node in config.NODES:
            try:
                await self.bot.slate.create_node(cls=getattr(slate, node.pop('type')), **node)
            except slate.NodeConnectionError as e:
                print(f'[SLATE] {e}')
            else:
                print(f'[SLATE] Node \'{node["identifier"]}\' connected.')
    """

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
            track = await event.player.node.decode_track(track_id=event.track_id)
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
            track = await event.player.node.decode_track(track_id=event.track_id)
        except slate.HTTPError:
            pass

        title = getattr(track or event.player.current, 'title', 'Not Found')
        await event.player.send(f'Something went wrong while playing the track `{title}`. Use `{config.PREFIX}support` for more help.')

        event.player.track_end_event.set()
        event.player.track_end_event.clear()

        event.player.skip_request_ids.clear()

    #

    @commands.command(name='join', aliases=['connect', 'summon'])
    @is_connected()
    async def join(self, ctx: context.Context) -> None:
        """
        Summons the bot to the voice channel that you are in.
        """

        if ctx.voice_client and ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am already in a voice channel.')

        if ctx.voice_client:
            await ctx.voice_client.reconnect(channel=ctx.author.voice.channel)
            await ctx.reply(f'Reconnected to the voice channel `{ctx.author.voice.channel}`')
        else:
            await self.bot.slate.create_player(channel=ctx.author.voice.channel, cls=Player)
            await ctx.reply(f'Joined the voice channel `{ctx.author.voice.channel}`.')

        ctx.voice_client.text_channel = ctx.channel

    @commands.group(name='play', aliases=['p'], invoke_without_command=True)
    @is_connected(same_channel=True)
    @has_voice_client(try_join=True)
    async def play(self, ctx: context.Context, *, query: str) -> None:
        """
        Queues a track with the given name or url.

        `query`: The query to search for tracks with.

        This command supports youtube/soundcloud searching or youtube, soundcloud, spotify, bandcamp, beam, twitch, and vimeo links.
        """

        async with ctx.channel.typing():

            search = await ctx.voice_client.search(query=query, ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in config.OWNER_IDS:
                raise exceptions.VoiceError('You are not able to play tracks from `HTTP` sources.')

            if search.source == 'spotify':
                tracks = search.tracks

                message = f'Added the Spotify {search.search_type} `{search.search_result.name}` to the queue.'
                if search.search_type in ('album', 'playlist'):
                    message = f'{message[:-1]} with a total of `{len(search.tracks)}` tracks.'

            else:

                if search.search_type == 'track':
                    tracks = [search.tracks[0]]
                    message = f'Added the {search.source} {search.search_type} `{search.tracks[0].title}` to the queue.'
                else:
                    tracks = search.tracks
                    message = f'Added the {search.source} {search.search_type} `{search.search_result.name}` to the queue with a total of **{len(search.tracks)}** tracks.'

            ctx.voice_client.queue.put(items=tracks)
            await ctx.reply(message)

    @play.command(name='soundcloud', aliases=['sc'])
    @is_connected(same_channel=True)
    @has_voice_client(try_join=True)
    async def play_soundcloud(self, ctx: context.Context, *, query: str) -> None:
        """
        Queues a track from soundcloud with the given name/url.

        `query`: The query to search for tracks with.
        """

        async with ctx.channel.typing():

            search = await ctx.voice_client.search(query=f'soundcloud:{query}', ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in config.OWNER_IDS:
                raise exceptions.VoiceError('You are not able to play tracks from `HTTP` sources.')

            if search.search_type == 'track':
                tracks = [search.tracks[0]]
                message = f'Added the {search.source} {search.search_type} `{search.tracks[0].title}` to the queue.'
            else:
                tracks = search.tracks
                message = f'Added the {search.source} {search.search_type} `{search.search_result.name}` to the queue with a total of **{len(search.tracks)}** tracks.'

            ctx.voice_client.queue.put(items=tracks)
            await ctx.reply(message)

    @play.command(name='music', aliases=['m'])
    @is_connected(same_channel=True)
    @has_voice_client(try_join=True)
    async def play_music(self, ctx: context.Context, *, query: str) -> None:
        """
        Queues a track from youtube music with the given name/url.

        `query`: The query to search for tracks with.
        """

        async with ctx.channel.typing():

            search = await ctx.voice_client.search(query=f'ytmsearch:{query}', ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in config.OWNER_IDS:
                raise exceptions.VoiceError('You are not able to play tracks from `HTTP` sources.')

            if search.search_type == 'track':
                tracks = [search.tracks[0]]
                message = f'Added the Youtube Music {search.search_type} `{search.tracks[0].title}` to the queue.'
            else:
                tracks = search.tracks
                message = f'Added the Youtube Music {search.search_type} `{search.search_result.name}` to the queue with a total of **{len(search.tracks)}** tracks.'

            ctx.voice_client.queue.put(items=tracks)
            await ctx.reply(message)

    @commands.command(name='playnext', aliases=['pnext', 'playtop', 'ptop'])
    @is_connected(same_channel=True)
    @has_voice_client(try_join=True)
    async def playtop(self, ctx: context.Context, *, query: str) -> None:
        """
        Queues a track at the beginning of the queue.

        `query`: The query to search for tracks with.

        This command supports youtube/soundcloud searching or youtube, soundcloud, spotify, bandcamp, beam, twitch, and vimeo links.
        """

        async with ctx.channel.typing():

            search = await ctx.voice_client.search(query=query, ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in config.OWNER_IDS:
                raise exceptions.VoiceError('You are not able to play tracks from `HTTP` sources.')

            if search.source == 'spotify':
                tracks = search.tracks

                message = f'Added the Spotify {search.search_type} `{search.search_result.name}` to the beginning of the queue.'
                if search.search_type in ('album', 'playlist'):
                    message = f'{message[:-1]} with a total of `{len(search.tracks)}` tracks.'

            else:

                if search.search_type == 'track':
                    tracks = [search.tracks[0]]
                    message = f'Added the {search.source} {search.search_type} `{search.tracks[0].title}` to the beginning of the queue.'
                else:
                    tracks = search.tracks
                    message = f'Added the {search.source} {search.search_type} `{search.search_result.name}` to the beginning of the queue with a total of **{len(search.tracks)}** tracks.'

            ctx.voice_client.queue.put(items=tracks, position=0)
            await ctx.reply(message)

    @commands.command(name='playnow', aliases=['pnow', 'playskip', 'pskip'])
    @is_connected(same_channel=True)
    @has_voice_client(try_join=True)
    async def playskip(self, ctx: context.Context, *, query: str) -> None:
        """
        Plays/queues a track and skips the current track.

        `query`: The query to search for tracks with.

        This command supports youtube/soundcloud searching or youtube, soundcloud, spotify, bandcamp, beam, twitch, and vimeo links.
        """

        async with ctx.channel.typing():

            search = await ctx.voice_client.search(query=query, ctx=ctx)

            if search.source == 'HTTP' and ctx.author.id not in config.OWNER_IDS:
                raise exceptions.VoiceError('You are not able to play tracks from `HTTP` sources.')

            if search.source == 'spotify':
                tracks = search.tracks

                message = f'Added the Spotify {search.search_type} `{search.search_result.name}` to the beginning of the queue.'
                if search.search_type in ('album', 'playlist'):
                    message = f'{message[:-1]} with a total of `{len(search.tracks)}` tracks.'

            else:

                if search.search_type == 'track':
                    tracks = [search.tracks[0]]
                    message = f'Added the {search.source} {search.search_type} `{search.tracks[0].title}` to the beginning of the queue.'
                else:
                    tracks = search.tracks
                    message = f'Added the {search.source} {search.search_type} `{search.search_result.name}` to the beginning of the queue with a total of **{len(search.tracks)}** tracks.'

            ctx.voice_client.queue.put(items=tracks, position=0)
            await ctx.reply(message)
            await ctx.voice_client.stop()
            await ctx.reply('Skipped the current track.')

    @commands.command(name='disconnect', aliases=['dc', 'leave'])
    @is_connected(same_channel=True)
    @has_voice_client()
    async def disconnect(self, ctx: context.Context) -> None:
        """
        Disconnects the bot from the voice channel that it is in.

        This command only temporarily disconnects the player, the current queue and other settings will remain after the bot has joined back.
        """

        await ctx.reply(f'Temporarily left the voice channel `{ctx.voice_client.channel}`.')
        await ctx.voice_client.stop()
        await ctx.voice_client.disconnect()

    @commands.command(name='destroy')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def destroy(self, ctx: context.Context) -> None:
        """
        Destroys the player.
        """

        await ctx.reply(f'Left the voice channel `{ctx.voice_client.channel}`.')
        await ctx.voice_client.destroy()

    @commands.command(name='skip', aliases=['next', 'stop', 's'])
    @is_voice_client_playing()
    @is_connected(same_channel=True)
    @has_voice_client()
    async def skip(self, ctx: context.Context, amount: int = 1) -> None:
        """
        Skips one, or an optional amount of tracks.

        `amount`: The amount of tracks to skip. Defaults to 1.
        """
        # sourcery no-metrics

        if ctx.voice_client.current.requester.id != ctx.author.id and ctx.author.id not in config.OWNER_IDS:

            if ctx.author not in ctx.voice_client.listeners:
                raise exceptions.VoiceError('You can not vote to skip as you are currently deafened.')

            if ctx.author.id in ctx.voice_client.skip_request_ids:
                ctx.voice_client.skip_request_ids.remove(ctx.author.id)
                message = 'Removed your vote to skip.'
            else:
                ctx.voice_client.skip_request_ids.add(ctx.author.id)
                message = 'Added your vote to skip.'

            skips_needed = (len(ctx.voice_client.listeners) // 2) + 1
            await ctx.reply(f'{message} Currently on `{len(ctx.voice_client.skip_request_ids)}` out of `{skips_needed}` votes needed to skip.')

            if len(ctx.voice_client.skip_request_ids) >= (len(ctx.voice_client.listeners) // 2) + 1:
                await ctx.voice_client.stop()
                await ctx.reply('Skipped the current track.')

        else:

            if amount == 1:
                await ctx.voice_client.stop()
                await ctx.reply('Skipped the current track.')

            else:

                if amount <= 0 or amount > len(ctx.voice_client.queue) + 1:
                    raise exceptions.VoiceError(f'There are not enough tracks in the queue to skip that many. Choose a number between `1` and `{len(ctx.voice_client.queue) + 1}`.')

                for track in ctx.voice_client.queue[:amount - 1]:
                    if track.requester.id != ctx.author.id and ctx.author.id not in config.OWNER_IDS:
                        raise exceptions.VoiceError(f'You are not the requester of all `{amount}` of the next tracks in the queue.')

                for _ in enumerate(ctx.voice_client.queue[:amount - 1]):
                    ctx.voice_client.queue.get()

                await ctx.voice_client.stop()
                await ctx.reply(f'Skipped `{amount}` {"track." if amount == 1 else "tracks."}')

    @commands.command(name='pause')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def pause(self, ctx: context.Context) -> None:
        """
        Pauses the current track.
        """

        if ctx.voice_client.is_paused:
            raise exceptions.VoiceError('The player is already paused.')

        await ctx.voice_client.set_pause(pause=True)
        await ctx.reply('The player is now paused.')

    @commands.command(name='resume', aliases=['continue', 'unpause'])
    @is_connected(same_channel=True)
    @has_voice_client()
    async def resume(self, ctx: context.Context) -> None:
        """
        Resumes the current track.
        """

        if ctx.voice_client.is_paused is False:
            raise exceptions.VoiceError('The player is not paused.')

        await ctx.voice_client.set_pause(pause=False)
        await ctx.reply('The player is now resumed.')

    @commands.command(name='seek')
    @is_voice_client_playing()
    @is_connected(same_channel=True)
    @has_voice_client()
    async def seek(self, ctx: context.Context, seconds: int = None) -> None:
        """
        Seeks to a position on the current track.

        `seconds`: The position to seek too, in seconds.
        """

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        if not seconds and seconds != 0:
            await ctx.reply(f'The players position is `{utils.format_seconds(seconds=round(ctx.voice_client.position // 1000))}`')
            return

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.voice_client.current.length:
            raise exceptions.VoiceError(f'That was not a valid position. Please choose a value between `0` and `{round(ctx.voice_client.current.length / 1000)}`.')

        await ctx.voice_client.set_position(position=milliseconds)
        await ctx.reply(f'The players position is now `{utils.format_seconds(seconds=milliseconds // 1000)}`.')

    @commands.command(name='replay')
    @is_voice_client_playing()
    @is_connected(same_channel=True)
    @has_voice_client()
    async def replay(self, ctx: context.Context) -> None:
        """
        Seeks to the start of the current track.

        `seconds`: The position to seek too, in seconds.
        """

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        await ctx.voice_client.set_position(position=0)
        await ctx.reply(f'The players position is now `{utils.format_seconds(seconds=0)}`.')

    @commands.command(name='volume', aliases=['vol'])
    @is_connected(same_channel=True)
    @has_voice_client()
    async def volume(self, ctx: context.Context, volume: int = None) -> None:
        """
        Changes the volume of the player.

        `volume`: The volume to change too, between 0 and 100.
        """

        if not volume and volume != 0:
            await ctx.reply(f'The players volume is `{ctx.voice_client.volume}%`.')
            return

        if volume < 0 or volume > 100 and ctx.author.id not in config.OWNER_IDS:
            raise exceptions.VoiceError('That was not a valid volume, Please choose a value between `0` and `100`.')

        await ctx.voice_client.set_volume(volume=volume)
        await ctx.reply(f'The players volume is now `{ctx.voice_client.volume}%`.')

    @commands.command(name='nowplaying', aliases=['np'])
    @is_voice_client_playing()
    @has_voice_client()
    async def nowplaying(self, ctx: context.Context) -> None:
        """
        Displays information about the current track.
        """

        await ctx.voice_client.invoke_controller()

    @commands.command(name='lyrics')
    async def lyrics(self, ctx: context.Context, *, query: str = 'spotify') -> None:

        if query == 'spotify':

            if (spotify_activity := discord.utils.find(lambda activity: isinstance(activity, discord.Spotify), ctx.author.activities)) is not None:
                query = f'{spotify_activity.title} - {spotify_activity.artist}'
            else:
                raise exceptions.VoiceError('You do not have an active spotify status to get the current track from.')

        elif query == 'player':

            if not ctx.voice_client or not ctx.voice_client.is_connected:
                raise exceptions.VoiceError('I am not connected to any voice channels.')
            if not ctx.voice_client.is_playing:
                raise exceptions.VoiceError('There are no tracks playing.')

            query = f'{ctx.voice_client.current.title} - {ctx.voice_client.current.requester}'

        try:
            results = await self.bot.ksoft.music.lyrics(query=query, limit=50)
        except ksoftapi.NoResults:
            raise exceptions.ArgumentError(f'No results were found for the query `{query}`.')
        except ksoftapi.APIError:
            raise exceptions.VoiceError('The API used to fetch lyrics is currently down/broken.')

        choice = await ctx.choice(
                entries=[f'`{index + 1}.` {result.name} - {result.artist}' for index, result in enumerate(results)], per_page=10,
                header=f'**__Please choose the number of the track you would like lyrics for:__**\n`Query`: {query}\n\n'
        )
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

        await ctx.paginate_embed(entries=entries, per_page=1, header=f'**Lyrics for `{result.name}` by `{result.artist}`:**\n\n', footer='\n\n*Lyrics provided by KSoft.Si API.*')

    #

    @commands.group(name='queue', aliases=['q'], invoke_without_command=True)
    @has_voice_client()
    async def queue(self, ctx: context.Context) -> None:
        """
        Displays the queue.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        time = utils.format_seconds(seconds=round(sum(track.length for track in ctx.voice_client.queue)) // 1000, friendly=True)
        header = f'Showing `{min([10, len(ctx.voice_client.queue)])}` out of `{len(ctx.voice_client.queue)}` track(s) in the queue. Total queue time is `{time}`.\n\n'

        entries = [
            f'`{index + 1}.` [{str(track.title)}]({track.uri}) | {utils.format_seconds(seconds=round(track.length) // 1000)} | {track.requester.mention}'
            for index, track in enumerate(ctx.voice_client.queue)
        ]

        await ctx.paginate_embed(entries=entries, per_page=10, title='Queue:', header=header)

    @queue.command(name='detailed', aliases=['d'])
    @has_voice_client()
    async def queue_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queue.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        entries = []
        for index, track in enumerate(ctx.voice_client.queue):
            embed = discord.Embed(colour=ctx.colour)
            embed.set_image(url=track.thumbnail)
            embed.description = f'''
            Showing detailed information about track `{index + 1}` out of `{len(ctx.voice_client.queue)}` in the queue.
            
            [{track.title}]({track.uri})\n\n`Author:` {track.author}\n`Source:` {track.source}
            `Length:` {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}
            `Live:` {track.is_stream}\n`Seekable:` {track.is_seekable}\n`Requester:` {track.requester.mention}
            '''
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @queue.group(name='history', aliases=['h'], invoke_without_command=True)
    @has_voice_client()
    async def queue_history(self, ctx: context.Context) -> None:
        """
        Displays the queue history.
        """

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
    @has_voice_client()
    async def queue_history_detailed(self, ctx: context.Context) -> None:
        """
        Displays detailed information about the queue history.
        """

        history = list(ctx.voice_client.queue.history)
        if not history:
            raise exceptions.VoiceError('The queue history is empty.')

        entries = []
        for index, track in enumerate(history):
            embed = discord.Embed(colour=ctx.colour)
            embed.set_image(url=track.thumbnail)
            embed.description = f'''
            Showing detailed information about track `{index + 1}` out of `{len(history)}` in the queue history.
            
            [{track.title}]({track.uri})
            
            `Author:` {track.author}\n`Source:` {track.source}
            `Length:` {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}
            `Live:` {track.is_stream}\n`Seekable:` {track.is_seekable}\n`Requester:` {track.requester.mention}
            '''
            entries.append(embed)

        await ctx.paginate_embeds(entries=entries)

    @commands.group(name='loop', invoke_without_command=True)
    @is_connected(same_channel=True)
    @has_voice_client()
    async def loop(self, ctx: context.Context) -> None:
        """
        Loops the whole queue.
        """

        ctx.voice_client.queue.set_looping(looping=not ctx.voice_client.queue.is_looping, current=False)
        await ctx.reply(f'I will {"start" if ctx.voice_client.queue.is_looping else "stop"} looping the whole queue.')

    @loop.command(name='current')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def loop_current(self, ctx: context.Context) -> None:
        """
        Loops the current track.
        """

        ctx.voice_client.queue.set_looping(looping=not ctx.voice_client.queue.is_looping, current=not ctx.voice_client.queue.is_looping_current)
        await ctx.reply(f'I will {"start" if ctx.voice_client.queue.is_looping_current else "stop"} looping the current track.')

    @commands.command(name='clear')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def clear(self, ctx: context.Context) -> None:
        """
        Clears the queue.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        ctx.voice_client.queue.clear()
        await ctx.reply('The queue has been cleared.')

    @commands.command(name='shuffle')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def shuffle(self, ctx: context.Context) -> None:
        """
        Shuffles the queue.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        ctx.voice_client.queue.shuffle()
        await ctx.reply('The queue has been shuffled.')

    @commands.command(name='reverse')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def reverse(self, ctx: context.Context) -> None:
        """
        Reverses the queue.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        ctx.voice_client.queue.reverse()
        await ctx.reply('The queue has been reversed.')

    @commands.command(name='sort')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def sort(self, ctx: context.Context, method: Literal['title', 'length', 'author'], reverse: bool = False) -> None:
        """
        Sorts the queue.

        `method`: The method to sort the queue with. Can be `title`, `length` or `author`.
        `reverse`: Whether to reverse the sort, as in `5, 3, 2, 4, 1` -> `5, 4, 3, 2, 1` instead of `5, 3, 2, 4, 1` -> `1, 2, 3, 4, 5`.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        if method == 'title':
            ctx.voice_client.queue._queue.sort(key=lambda track: track.title, reverse=reverse)
        elif method == 'author':
            ctx.voice_client.queue._queue.sort(key=lambda track: track.author, reverse=reverse)
        elif method == 'length':
            ctx.voice_client.queue._queue.sort(key=lambda track: track.length, reverse=reverse)

        await ctx.reply(f'The queue has been sorted with method `{method}`.')

    @commands.command(name='remove')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def remove(self, ctx: context.Context, entry: int = 0) -> None:
        """
        Removes a track from the queue.

        `entry`: The position of the track you want to remove.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        if entry <= 0 or entry > len(ctx.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry. Choose a number between `1` and `{len(ctx.voice_client.queue)}` ')

        item = ctx.voice_client.queue.get(position=entry - 1, put_history=False)
        await ctx.reply(f'Removed `{item.title}` from the queue.')

    @commands.command(name='move')
    @is_connected(same_channel=True)
    @has_voice_client()
    async def move(self, ctx: context.Context, entry_1: int = 0, entry_2: int = 0) -> None:
        """
        Move a track in the queue to a different position.

        `entry_1`: The position of the track you want to move from.
        `entry_2`: The position of the track you want to move too.
        """

        if ctx.voice_client.queue.is_empty:
            raise exceptions.VoiceError('The queue is empty.')

        if entry_1 <= 0 or entry_1 > len(ctx.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry to move from. Choose a number between `1` and `{len(ctx.voice_client.queue)}` ')

        if entry_2 <= 0 or entry_2 > len(ctx.voice_client.queue):
            raise exceptions.VoiceError(f'That was not a valid track entry to move too. Choose a number between `1` and `{len(ctx.voice_client.queue)}` ')

        track = ctx.voice_client.queue.get(position=entry_1 - 1, put_history=False)
        ctx.voice_client.queue.put(items=track, position=entry_2 - 1)
        await ctx.reply(f'Moved `{track.title}` from position `{entry_1}` to position `{entry_2}`.')


def setup(bot: Life) -> None:
    bot.add_cog(Music(bot=bot))
