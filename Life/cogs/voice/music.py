"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

import asyncio
import re

import diorite
import humanize
import json
import discord
import spotify
from discord.ext import commands

from cogs.utilities.exceptions import LifeVoiceError
from cogs.voice.utilities.player import Player
from cogs.voice.utilities import objects


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.diorite = diorite.Client(bot=self.bot, session=self.bot.session, loop=self.bot.loop)
        self.bot.spotify_http = spotify.HTTPClient(client_id=self.bot.config.spotify_app_id,
                                                   client_secret=self.bot.config.spotify_secret)
        self.bot.spotify = spotify.Client(client_id=self.bot.config.spotify_app_id,
                                          client_secret=self.bot.config.spotify_secret)

        self.bot.spotify_url_regex = re.compile(r'https://open.spotify.com?.+(album|playlist|track)/([a-zA-Z0-9]+)')
        self.bot.youtube_url_regex = re.compile(r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be).+$')

        asyncio.create_task(self.load())

    @commands.Cog.listener()
    async def on_diorite_track_start(self, event: diorite.TrackStartEvent):
        self.bot.dispatch('life_track_start', event.player.guild.id)

    @commands.Cog.listener()
    async def on_diorite_track_end(self, event: diorite.TrackEndEvent):
        self.bot.dispatch('life_track_end', event.player.guild.id)

    @commands.Cog.listener()
    async def on_diorite_track_stuck(self, event: diorite.TrackStuckEvent):
        self.bot.dispatch('life_track_end', event.player.guild.id)
        await event.player.channel.send(f'The current track got stuck while playing. This should not happen so you'
                                        f'should use `{self.bot.config.prefix}support` for more help.')

    @commands.Cog.listener()
    async def on_diorite_track_error(self, event: diorite.TrackExceptionEvent):
        self.bot.dispatch('life_track_end', event.player.guild.id)
        await event.player.channel.send(f'Something went wrong while playing a track. Error: `{event.error}`')

    @commands.Cog.listener()
    async def on_diorite_websocket_closed(self, event: diorite.WebSocketClosedEvent):
        if event.code == 1000:
            return
        await event.player.channel.send(f'Your nodes websocket decided to disconnect, This should not happen so you'
                                        f'should use `{self.bot.config.prefix}support` for more help.')
        await event.player.destroy()
        event.player.task.cancel()

    async def unload(self):

        if self.bot.redis is None:
            print('[PLAYER RETENTION] Redis not connected, Queue retention disabled')
            return

        if not self.bot.diorite.players:
            print('[PLAYER RETENTION] Found no players to save.')
            return

        players = [player for player in self.bot.diorite.players.copy().values() if player.is_connected]
        print(f'[PLAYER RETENTION] Found \'{len(players)}\' player(s) to save.')
        for player in players:

            current_track = None
            if player.current:
                current_track = {'track_id': player.current.track_id, 'info': player.current.info,
                                 'requester_id': player.current.requester.id, 'source': player.current.source}

            queue_tracks = None
            if not player.queue.is_empty:
                queue_tracks = [{'track_id': track.track_id, 'info': track.info,
                                 'requester_id': track.requester.id, 'source': track.source}
                                for track in player.queue.queue_list]

            player_data = {
                'voice_channel_id': player.voice_channel.id,
                'volume': player.volume,
                'paused': player.paused,
                'current': json.dumps(current_track),
                'position': player.position,
                'queue': json.dumps(queue_tracks),
                'looping': player.looping,
                'text_channel_id': player.text_channel.id
            }

            player_json = json.dumps(player_data)

            await self.bot.redis.hset(f'player_retention_{self.bot.user.id}', player.guild.id, player_json)
            print(f'[PLAYER RETENTION] Player: \'{player.guild.id}\' saved.')

        for player in self.bot.diorite.players.copy().values():
            await player.teardown()

    async def load(self):

        for node in self.bot.config.node_info.values():
            try:
                await self.bot.diorite.create_node(**node)
                print(f'[DIORITE] Node {node["identifier"]} connected.')
            except diorite.NodeCreationError as e:
                print(f'[DIORITE] {e}')
            except diorite.NodeConnectionError as e:
                print(f'[DIORITE] {e}')

        if not self.bot.diorite.nodes:
            print('\n[PLAYER RETENTION] No lavalink nodes connected, player retention disabled.')
            return

        if self.bot.redis is None:
            print('\n[PLAYER RETENTION] Redis not connected, player retention disabled.')
            return

        players = await self.bot.redis.hgetall(f'player_retention_{self.bot.user.id}')

        if not players:
            print('\n[PLAYER RETENTION] Found no players to load.')
            return

        print(f'\n[PLAYER RETENTION] Found \'{len(players)}\' player(s) to load.')

        for guild_id, player_json in players.items():

            guild_id = guild_id.decode('utf-8')
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                await self.bot.redis.hdel(f'player_retention_{self.bot.user.id}', guild_id)
                print(f'[PLAYER RETENTION] Guild: \'{guild_id}\' is no longer available.')
                continue

            player_data = json.loads(player_json)
            print(f'[PLAYER RETENTION] Player: \'{guild_id}\' attempting load.')

            voice_channel_id = player_data.get('voice_channel_id')
            voice_channel = self.bot.get_channel(voice_channel_id)
            if not voice_channel:
                await self.bot.redis.hdel(f'player_retention_{self.bot.user.id}', guild.id)
                print(f'[PLAYER RETENTION] Voice channel: \'{voice_channel_id}\' is no longer available.')
                continue

            text_channel_id = player_data.get('text_channel_id')
            text_channel = self.bot.get_channel(text_channel_id)
            if not text_channel:
                await self.bot.redis.hdel(f'player_retention_{self.bot.user.id}', guild.id)
                print(f'[PLAYER RETENTION] Text channel: \'{voice_channel_id}\' is no longer available.')
                continue

            player = self.bot.diorite.get_player(guild, cls=Player)
            player.text_channel = text_channel
            await player.connect(voice_channel)

            await player.channel.send('The bot restarted while you were playing music, attempting to reload.')

            looping = player_data.get('looping')
            if looping is True:
                player.looping = True

            volume = player_data.get('volume')
            if volume != 100:
                await player.set_volume(volume)

            current_json = player_data.get('current')
            if current_json != 'null':

                track_data = json.loads(current_json)

                current_requester_id = track_data.get('requester_id')
                current_requester = guild.get_member(current_requester_id)
                if not current_requester:
                    print(f'[PLAYER RETENTION] Track requester: \'{current_requester_id}\' is no longer available.')
                    current_requester = guild.get_member(guild.owner.id)

                track = objects.LifeTrack(track_id=track_data.get('track_id'), info=track_data.get('info'),
                                          requester=current_requester)
                player.queue.put(track)

                try:
                    await self.bot.wait_for('life_track_start', timeout=10.0, check=lambda g: g == player.guild.id)
                except asyncio.TimeoutError:
                    continue
                else:

                    paused = player_data.get('paused')
                    if paused is True:
                        await player.set_pause(True)

                    position = player_data.get('position')
                    if position != 0:
                        await player.seek(position)

            queue_json = player_data.get('queue')
            if queue_json != 'null':

                queue_data = json.loads(queue_json)

                for track_data in queue_data:

                    track_requester_id = track_data.get('requester_id')
                    track_requester = guild.get_member(track_requester_id)
                    if not track_requester:
                        track_requester = guild.get_member(guild.owner.id)

                    if track_data.get('source') == 'youtube':
                        track = objects.LifeTrack(track_id=track_data.get('track_id'), info=track_data.get('info'),
                                                  requester=track_requester)
                    else:
                        track = objects.SpotifyTrack(info=track_data.get('info'), requester=track_requester)

                    player.queue.put(track)

            await player.channel.send('Player was successfully reloaded.')
            print(f'[PLAYER RETENTION] Player: \'{guild_id}\' successfully loaded.')

            await self.bot.redis.hdel(f'player_retention_{self.bot.user.id}', guild.id)

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx):
        """
        Joins your voice channel.
        """

        channel = getattr(ctx.author.voice, 'channel')
        if not channel:
            raise LifeVoiceError('You must be in a voice channel to use this command.')

        if ctx.player.is_connected:

            if channel.id != ctx.player.voice_channel.id:
                raise LifeVoiceError(f'I am already in the voice channel `{ctx.player.voice_channel}`.')

            raise LifeVoiceError('I am already in your voice channel.')

        ctx.player.text_channel = ctx.channel
        await ctx.player.connect(channel)
        return await ctx.send(f'Joined your voice channel `{channel}`.')

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        """
        Plays/queues a track with the given search. Supports spotify.

        `query`: The name/link of the track you want to play. Spotify links will search youtube with the track name.
        """

        if not ctx.player.is_connected:
            await ctx.invoke(self.join)
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        async with ctx.channel.typing():

            search = await ctx.player.search(requester=ctx.author, search=query)

            if search.source == 'spotify':

                if search.source_type == 'track':
                    message = f'Added the spotify track **{search.result.name}** to the queue.'
                elif search.source_type in ('album', 'playlist'):
                    message = f'Added the spotify {search.source_type} **{search.result.name}** to the queue ' \
                              f'with a total of **{len(search.tracks)}** track(s).'
                tracks = search.tracks

            elif search.source == 'youtube':

                if search.source_type == 'track':
                    message = f'Added the youtube track **{search.tracks[0].title}** to the queue.'
                    tracks = [search.tracks[0]]

                elif search.source_type == 'playlist':
                    message = f'Added the youtube playlist **{search.result.name}** to the queue ' \
                              f'with a total of **{len(search.tracks)}** track(s)'
                    tracks = search.tracks

            ctx.player.queue.extend(tracks)
            return await ctx.send(message)

    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        """
        Leaves the voice channel.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        ctx.player.queue.clear()
        ctx.player.task.cancel()

        await ctx.send(f'Left the voice channel `{ctx.guild.me.voice.channel}`.')
        return await ctx.player.destroy()

    @commands.command(name='skip', aliases=['stop'])
    async def skip(self, ctx, amount: int = 1):
        """
        Skips to the next track in the queue.

        `amount`: The amount of tracks to skip.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')
        if not ctx.player.is_playing:
            raise LifeVoiceError(f'There are no tracks currently playing.')

        if ctx.player.current.requester.id != ctx.author.id:
            raise LifeVoiceError('Yell at my owner to do vote skipping.')

        if amount <= 0 or amount > ctx.player.queue.size + 1:
            raise LifeVoiceError(f'There are not enough tracks in the queue to skip that many. Choose a number between'
                                 f'`1` and `{ctx.player.queue.size + 1}`.')

        for index, track in enumerate(ctx.player.queue.queue_list[:amount - 1]):
            if not track.requester.id == ctx.author.id:
                return await ctx.send(f'You only skipped `{index + 1}` out of the next `{amount}` tracks because you'
                                      f'were not the requester of all them.')
            await ctx.player.queue.get_pos(0)

        await ctx.player.stop()
        return await ctx.send(f'The current tracks requester has skipped `{amount}` track(s).')

    @commands.command(name='pause')
    async def pause(self, ctx):
        """
        Pauses the player.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.paused is True:
            raise LifeVoiceError('The player is already paused.')

        await ctx.player.set_pause(True)
        return await ctx.send(f'The player is now paused.')

    @commands.command(name='unpause', aliases=['resume'])
    async def unpause(self, ctx):
        """
        Resumes the player.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.paused is False:
            raise LifeVoiceError('The player is not paused.')

        await ctx.player.set_pause(False)
        return await ctx.send(f'The player is now un-paused')

    @commands.command(name='seek')
    async def seek(self, ctx, seconds: int = None):
        """
        Changes the position of the player.

        `position`: The position to seek the track to in seconds.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')
        if not ctx.player.is_playing:
            raise LifeVoiceError(f'There are no tracks currently playing.')

        if not ctx.player.current.is_seekable:
            raise LifeVoiceError('This track is not seekable.')

        if not seconds and not seconds == 0:
            return await ctx.send(f'The current tracks position is '
                                  f'`{self.bot.utils.format_time(ctx.player.position / 1000)}`')

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.player.current.length:
            raise LifeVoiceError(f'The current track is not long enough the seek to that position. Please choose a '
                                 f'number between `1` and `{round(ctx.player.current.length / 1000)}`.')

        await ctx.player.seek(milliseconds)
        return await ctx.send(f'The current tracks position is now '
                              f'`{self.bot.utils.format_time(milliseconds / 1000)}`.')

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int = None):
        """
        Changes the volume of the player.

        `volume`: The volume to change too, between 0 and 100.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if not volume and not volume == 0:
            return await ctx.send(f'The players current volume is `{ctx.player.volume}%`.')

        if volume < 0 or volume > 100:
            raise LifeVoiceError(f'That was not a valid volume, Please choose a number between `1` and and `100`.')

        await ctx.player.set_volume(volume)
        return await ctx.send(f'The players volume is now `{ctx.player.volume}%`.')

    @commands.command(name='now_playing', aliases=['np'])
    async def now_playing(self, ctx):
        """
        Displays the music controller
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        if not ctx.player.is_playing:
            raise LifeVoiceError(f'There are no tracks currently playing.')

        return await ctx.player.invoke_controller(ctx.channel)

    @commands.command(name='queue', aliases=["q"])
    async def queue(self, ctx):
        """
        Displays the players queue.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        if not ctx.player.is_playing:
            raise LifeVoiceError(f'There are no tracks currently playing.')

        if ctx.player.queue.is_empty:
            raise LifeVoiceError('The players queue is empty.')

        title = f'__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | ' \
                f'`{self.bot.utils.format_time(round(ctx.player.current.length) / 1000)}` | ' \
                f'`Requested by:` {ctx.player.current.requester.mention}\n\n' \
                f'__**Up next:**__: Showing `{min([10, ctx.player.queue.size])}` out of ' \
                f'`{ctx.player.queue.size}` track(s) in the queue.\n'

        entries = []
        for index, track in enumerate(ctx.player.queue.queue_list):
            entries.append(f'**{index + 1}.** [{str(track.title)}]({track.uri}) | '
                           f'`{self.bot.utils.format_time(round(track.length) / 1000)}` | '
                           f'`Requested by:` {track.requester.mention}\n')

        time = sum(track.length for track in ctx.player.queue.queue_list)

        footer = f'\nThere are `{ctx.player.queue.size}` track(s) in the queue ' \
                 f'with a total time of `{self.bot.utils.format_time(round(time) / 1000)}`'

        return await ctx.paginate_embed(header=title, footer=footer, entries=entries, entries_per_page=10)

    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        """
        Shuffles the players queue.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.queue.is_empty:
            raise LifeVoiceError('The players queue is empty.')

        ctx.player.queue.shuffle()
        return await ctx.send(f'The queue has been shuffled.')

    @commands.command(name='clear')
    async def clear(self, ctx):
        """
        Clears the players queue.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.queue.is_empty:
            raise LifeVoiceError('The players queue is empty.')

        ctx.player.queue.clear()
        return await ctx.send(f'The queue has been cleared.')

    @commands.command(name='reverse')
    async def reverse(self, ctx):
        """
        Reverses the players queue.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.queue.is_empty:
            raise LifeVoiceError('The players queue is empty.')

        ctx.player.queue.reverse()
        return await ctx.send(f'The queue has been reversed.')

    @commands.command(name='loop', aliases=['repeat'])
    async def loop(self, ctx):
        """
        Loops the players queue.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.looping is True:
            ctx.player.looping = False
            return await ctx.send(f'The queue will stop looping.')

        ctx.player.looping = True
        return await ctx.send(f'The queue will start looping.')

    @commands.command(name='remove')
    async def remove(self, ctx, entry: int = 0):
        """
        Remove a track from the queue.

        `entry`: The position of the track you want to remove.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.queue.is_empty:
            raise LifeVoiceError('The players queue is empty.')

        if entry <= 0 or entry > ctx.player.queue.size:
            raise LifeVoiceError(f'That was not a valid track entry number. Choose a number between `1` and '
                                 f'`{ctx.player.queue.size + 1}` ')

        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f'Removed `{item.title}` from the queue.')

    @commands.command(name='move')
    async def move(self, ctx, entry_1: int = 0, entry_2: int = 0):
        """
        Move a track in the queue to a different position

        `entry_1`: The position of the track you want to move from.
        `entry_2`: The position of the track you want to move too.
        """

        if not ctx.player.is_connected:
            raise LifeVoiceError('I am not connected to any voice channels.')
        channel = getattr(ctx.author.voice, 'channel')
        if not channel or channel.id != ctx.player.voice_channel.id:
            raise LifeVoiceError(f'You must be connected to the same voice channel as me to use this command.')

        if ctx.player.queue.is_empty:
            raise LifeVoiceError('The players queue is empty.')

        if entry_1 <= 0 or entry_1 > ctx.player.queue.size:
            raise LifeVoiceError(f'That was not a valid track entry to move from. Choose a number between `1` and '
                                 f'`{ctx.player.queue.size + 1}` ')

        if entry_2 <= 0 or entry_2 > ctx.player.queue.size:
            raise LifeVoiceError(f'That was not a valid track entry to move too. Choose a number between `1` and '
                                 f'`{ctx.player.queue.size + 1}` ')

        item = await ctx.player.queue.get_pos(entry_1 - 1)
        ctx.player.queue.put_pos(item, entry_2 - 1)

        return await ctx.send(f'Moved `{item.title}` from position `{entry_1}` to position `{entry_2}`.')

    @commands.command(name='musicinfo', aliases=['mi'])
    async def musicinfo(self, ctx):
        """
        Display stats about the bots music cog.
        """

        uptime = self.bot.utils.format_time(round(ctx.player.node.stats.uptime / 1000), friendly=True)
        reservable = humanize.naturalsize(ctx.player.node.stats.memory_reservable)
        allocated = humanize.naturalsize(ctx.player.node.stats.memory_allocated)
        used = humanize.naturalsize(ctx.player.node.stats.memory_used)
        free = humanize.naturalsize(ctx.player.node.stats.memory_free)
        cpu_cores = ctx.player.node.stats.cpu_cores

        embed = discord.Embed(colour=discord.Color.gold())
        embed.add_field(name='Lavalink info:',
                        value=f'`Memory reservable:` {reservable}\n`Memory allocated:` {allocated}\n'
                              f'`Memory used:` {used}\n`Memory free:` {free}\n`CPU Cores:` {cpu_cores}\n'
                              f'`Uptime:` {uptime}')
        embed.add_field(name='\u200B', value='\u200B')
        embed.add_field(name='Diorite stats:',
                        value=f'`Version:` {diorite.__version__}\n`Players:` {len(self.bot.diorite.players)}\n'
                              f'`Nodes:` {len(self.bot.diorite.nodes)}')

        for node in self.bot.diorite.nodes.values():
            active_players = len([player for player in node.players.values() if player.is_connected])
            embed.add_field(name=f'Node: {node.identifier}',
                            value=f'`Players:` {len(node.players)}\n`Active players:` {active_players}')

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))
