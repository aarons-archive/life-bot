import asyncio
import re

import spotify
from discord.ext import commands

import diorite
from cogs.utilities import checks


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.diorite = diorite.Client(bot=self.bot, session=self.bot.session, loop=self.bot.loop)
        self.bot.http_spotify = spotify.HTTPClient(client_id=self.bot.config.SPOTIFY_ID,
                                                   client_secret=self.bot.config.SPOTIFY_SECRET)
        self.bot.spotify = spotify.Client(client_id=self.bot.config.SPOTIFY_ID,
                                          client_secret=self.bot.config.SPOTIFY_SECRET)

        self.bot.spotify_url_regex = re.compile(r'https://open.spotify.com?.+(album|playlist|track)/([a-zA-Z0-9]+)')
        self.bot.youtube_url_regex = re.compile(r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be).+$')
        asyncio.create_task(self.load_nodes())

    async def load_nodes(self):

        for node in self.bot.config.NODES.values():
            try:
                await self.bot.diorite.create_node(host=node['host'], password=node['password'],
                                                   port=node['port'], identifier=node['identifier'])
                print(f'[DIORITE] Node {node["identifier"]} connected.')
            except diorite.NodeCreationError as e:
                print(f'[DIORITE] {e}')
                continue
            except diorite.NodeConnectionError as e:
                print(f'[DIORITE] {e}')
                continue

    @commands.command(name='join', aliases=['connect'])
    @checks.is_member_connected()
    async def join(self, ctx):
        """
        Joins the author's voice channel.
        """

        channel = ctx.author.voice.channel

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(channel)
            return await ctx.send(f'Joined your voice channel `{channel}`.')

        if ctx.player.voice_channel.id != channel.id:
            return await ctx.send(f'I am already the voice channel `{ctx.player.voice_channel}`. '
                                  f'Please disconnect me from that channel and then use this command.')

        return await ctx.send('I am already in your voice channel.')

    @commands.command(name='play')
    @checks.is_member_connected()
    async def play(self, ctx, *, search: str):
        """
        Searches for and plays a track. Supports spotify.

        `search`: The name/link of the track you want to play. Spotify links will search youtube with the track name.
        """

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        if ctx.author.voice.channel != ctx.player.voice_channel:
            raise commands.CheckFailure(f'You are not connected to the same voice channel as me.')

        async with ctx.channel.typing():

            search_result = await ctx.player.search(ctx=ctx, search=search)

            search_type = search_result.get('type')
            result_type = search_result.get('return_type')
            result = search_result.get('result')
            tracks = search_result.get('tracks')

            if search_type == 'spotify':

                if result_type == 'track':
                    message = f'Added the spotify track **{result.name}** to the queue.'
                elif result_type == 'album':
                    message = f'Added the spotify album **{result.name}** to the queue ' \
                              f'with a total of **{len(tracks)}** track(s).'
                elif result_type == 'playlist':
                    message = f'Added the spotify playlist **{result.name}** to the queue ' \
                              f'with a total of **{len(tracks)}** track(s).'

                ctx.player.queue.extend(tracks)
                return await ctx.send(message)

            elif search_type == 'youtube':

                if result_type == 'playlist':
                    message = f'Added the youtube playlist **{result.name}** to the queue ' \
                              f'with a total of **{len(tracks)}** track(s)'
                    ctx.player.queue.extend(tracks)
                elif result_type == 'track':
                    message = f'Added the youtube track **{result[0].title}** to the queue.'
                    ctx.player.queue.extend([tracks[0]])

                return await ctx.send(message)

    @commands.command(name='leave', aliases=['disconnect'])
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def leave(self, ctx):
        """
        Leaves the voice channel.
        """

        ctx.player.queue.clear()
        ctx.player.task.cancel()
        await ctx.player.destroy()

        return await ctx.send(f'Left the voice channel `{ctx.guild.me.voice.channel}`.')

    @commands.command(name='skip', aliases=['stop'])
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def skip(self, ctx, amount: int = 1):
        """
        Skips to the next track in the queue.

        `amount`: The amount of tracks to skip. You must be the requester of all the tracks to do this.
        """

        if ctx.player.current.requester.id != ctx.author.id:
            return await ctx.send('https://cdn.discordapp.com/emojis/697246680084643951.png?v=1 <@238356301439041536>')

        if amount <= 0 or amount > ctx.player.queue.size + 1:
            return await ctx.send(f'There are not enough tracks in the queue to skip that many. Choose a number between'
                                  f'`1` and `{ctx.player.queue.size + 1}`.')

        for index, track in enumerate(ctx.player.queue.queue_list[:amount - 1]):
            if not track.requester.id == ctx.author.id:
                return await ctx.send(f'You only skipped `{index + 1}` out of the next `{amount}` tracks because you'
                                      f'were not the requester of all them.')
            await ctx.player.queue.get_pos(0)

        await ctx.player.stop()
        return await ctx.send(f'The current tracks requester has skipped `{amount}` track(s).')

    @commands.command(name='pause')
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def pause(self, ctx):
        """
        Pauses the player.
        """

        if ctx.player.is_paused:
            return await ctx.send('The player is already paused.')

        await ctx.player.set_pause(True)
        return await ctx.send(f'The player is now paused.')

    @commands.command(name='unpause', aliases=['resume'])
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def un_pause(self, ctx):
        """
        Un-pauses the player.
        """

        if not ctx.player.is_paused:
            return await ctx.send('The player is not paused.')

        await ctx.player.set_pause(False)
        return await ctx.send(f'The player is now un-paused')

    @commands.command(name='seek')
    @checks.is_player_playing()
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def seek(self, ctx, seconds: int = None):
        """
        Changes the position of the player.

        `position`: The position to seek the track to in seconds.
        """

        if not ctx.player.current.is_seekable:
            return await ctx.send('This track is not seekable.')

        if not seconds and not seconds == 0:
            return await ctx.send(f'The current tracks position is '
                                  f'`{self.bot.utils.format_time(ctx.player.position / 1000)}`')

        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.player.current.length:
            return await ctx.send(f'The current track is not long enough the seek to that position. Please choose a '
                                  f'number between `1` and `{round(ctx.player.current.length / 1000)}`.')

        await ctx.player.seek(milliseconds)
        return await ctx.send(f'The current tracks position is now '
                              f'`{self.bot.utils.format_time(milliseconds / 1000)}`.')

    @commands.command(name='volume', aliases=['vol'])
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def volume(self, ctx, volume: int = None):
        """
        Changes the volume of the player.

        `volume`: The volume to change too, between 0 and 100.
        """

        if not volume and not volume == 0:
            return await ctx.send(f'The players current volume is `{ctx.player.volume}%`.')

        if volume < 0 or volume > 100:
            return await ctx.send(f'That was not a valid volume, Please choose a number between `1` and and `100`.')

        await ctx.player.set_volume(volume)
        return await ctx.send(f'The players volume is now `{ctx.player.volume}%`.')

    @commands.command(name='now_playing', aliases=['np'])
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def now_playing(self, ctx):
        """
        Displays the music controller
        """

        if not ctx.player.current:
            return await ctx.send('The player is not currently playing anything.')

        return await ctx.player.invoke_controller(ctx.player.current)

    @commands.command(name='queue', aliases=["q"])
    @checks.is_player_connected()
    async def queue(self, ctx):
        """
        Displays the players queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send('The players queue is empty.')

        title = f'__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | ' \
                f'`{self.bot.utils.format_time(round(ctx.player.current.length) / 1000)}` | ' \
                f'`Requested by:` {ctx.player.current.requester.mention}\n\n' \
                f'__**Up next:**__: Showing `{min([10, ctx.player.queue.size])}` out of ' \
                f'`{ctx.player.queue.size}` track(s) in the queue.\n' \

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
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def shuffle(self, ctx):
        """
        Shuffles the players queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send('The players queue is empty.')

        ctx.player.queue.shuffle()
        return await ctx.send(f'The queue has been shuffled.')

    @commands.command(name='clear')
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def clear(self, ctx):
        """
        Clears the players queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send('The players queue is empty.')

        ctx.player.queue.clear()
        return await ctx.send(f'The queue has been cleared.')

    @commands.command(name='reverse')
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def reverse(self, ctx):
        """
        Reverses the players queue.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send('The players queue is empty.')

        ctx.player.queue.reverse()
        return await ctx.send(f'The queue has been reversed.')

    @commands.command(name='loop', aliases=['repeat'])
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def loop(self, ctx):
        """
        Loops the players queue.
        """

        if ctx.player.queue_loop is True:
            ctx.player.queue_loop = False
            return await ctx.send(f'The queue will stop looping.')

        ctx.player.queue_loop = True
        return await ctx.send(f'The queue will start looping.')

    @commands.command(name='remove')
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def remove(self, ctx, entry: int = 0):
        """
        Remove a track from the queue.

        `entry`: The position of the track you want to remove.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send('The players queue is empty.')

        if entry <= 0 or entry > ctx.player.queue.size:
            return await ctx.send(f'That was not a valid track entry number. Choose a number between `1` and '
                                  f'`{ctx.player.queue.size + 1}` ')

        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f'Removed `{item.title}` from the queue.')

    @commands.command(name='move')
    @checks.is_member_in_channel()
    @checks.is_member_connected()
    @checks.is_player_connected()
    async def move(self, ctx, entry_1: int = 0, entry_2: int = 0):
        """
        Move a track in the queue to a different position

        `entry_1`: The position of the track you want to move from.
        `entry_2`: The position of the track you want to move too.
        """

        if ctx.player.queue.is_empty:
            return await ctx.send('The players queue is empty.')

        if entry_1 <= 0 or entry_1 > ctx.player.queue.size:
            return await ctx.send(f'That was not a valid track entry to move from. Choose a number between `1` and '
                                  f'`{ctx.player.queue.size + 1}` ')

        if entry_2 <= 0 or entry_2 > ctx.player.queue.size:
            return await ctx.send(f'That was not a valid track entry to move too. Choose a number between `1` and '
                                  f'`{ctx.player.queue.size + 1}` ')

        item = await ctx.player.queue.get_pos(entry_1 - 1)
        ctx.player.queue.put_pos(item, entry_2 - 1)

        return await ctx.send(f'Moved `{item.title}` from position `{entry_1}` to position `{entry_2}`.')


def setup(bot):
    bot.add_cog(Music(bot))
