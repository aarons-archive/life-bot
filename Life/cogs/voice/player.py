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

import discord
from discord.ext import commands

import colours
import config
import slate
from bot import Life
from cogs.voice.custom.player import Player
from slate import obsidian
from utilities import checks, context, converters, exceptions, utils


class PlayerController(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    #

    async def load(self) -> None:

        print('')

        for node in config.NODES:
            try:
                await self.bot.slate.create_node(
                        type=obsidian.ObsidianNode, bot=self.bot, region=discord.VoiceRegion.us_east, **node,
                        spotify_client_id=config.SPOTIFY_CLIENT_ID, spotify_client_secret=config.SPOTIFY_CLIENT_SECRET
                )
            except slate.NodeConnectionError as e:
                print(f'[SLATE] {e}')
            else:
                print(f'[SLATE] Node \'{node["identifier"]}\' connected.')

    # TODO: Edit these

    @commands.Cog.listener()
    async def on_obsidian_track_start(self, player: Player, event: obsidian.ObsidianTrackStart) -> None:

        player._track_start_event.set()
        player._track_start_event.clear()

        await player.invoke_controller()

    @commands.Cog.listener()
    async def on_obsidian_track_end(self, player: Player, event: obsidian.ObsidianTrackEnd) -> None:

        player._track_end_event.set()
        player._track_end_event.clear()

    @commands.Cog.listener()
    async def on_obsidian_track_exception(self, player: Player, event: obsidian.ObsidianTrackException) -> None:

        track = None
        try:
            track = await player.node.decode_track(track_id=event.track_id)
        except slate.HTTPError:
            pass

        title = getattr(track or player.current, 'title', 'Not Found')
        await player.send(f'There was an error of severity `{event.severity}` while playing the track `{title}`.\nReason: {event.message}')

        player._track_end_event.set()
        player._track_end_event.clear()

    @commands.Cog.listener()
    async def on_obsidian_track_stuck(self, player: Player, event: obsidian.ObsidianTrackStuck) -> None:

        track = None
        try:
            track = await player.node.decode_track(track_id=event.track_id)
        except slate.HTTPError:
            pass

        title = getattr(track or player.current, 'title', 'Not Found')
        await player.send(f'Something went wrong while playing the track `{title}`. Use `{config.PREFIX}support` for more help.')

        player._track_end_event.set()
        player._track_end_event.clear()

    #

    @commands.command(name='nowplaying', aliases=['np'])
    @checks.is_voice_client_playing()
    @checks.has_voice_client()
    async def nowplaying(self, ctx: context.Context) -> None:
        """
        Shows information about the current track.
        """

        await ctx.voice_client.invoke_controller()

    @commands.command(name='save', aliases=['grab', 'yoink'])
    @checks.is_voice_client_playing()
    @checks.has_voice_client()
    async def save(self, ctx: context.Context) -> None:
        """
        Saves the current track to your DM's.
        """

        try:
            track = ctx.voice_client.current
            await ctx.author.send(
                    embed=discord.Embed(
                        colour=colours.MAIN,
                        title=track.title,
                        url=track.uri,
                        description=f'''
                        `Author:` {track.author}
                        `Source:` {track.source.value.title()}
                        `Length:` {utils.format_seconds(seconds=round(track.length) // 1000, friendly=True)}
                        `Live:` {track.is_stream}
                        `Seekable:` {track.is_seekable}'
                        '''
                    ).set_image(url=track.thumbnail)
            )
            await ctx.reply('Track saved to DM\'s.')

        except discord.Forbidden:
            raise exceptions.VoiceError('I am unable to DM you.')

    @commands.command(name='join', aliases=['summon', 'connect'])
    @checks.is_connected()
    async def join(self, ctx: context.Context) -> None:
        """
        Summons the bot to the voice channel that you are in.
        """

        if ctx.voice_client and ctx.voice_client.is_connected:
            raise exceptions.VoiceError('I am already in a voice channel.')

        await ctx.author.voice.channel.connect(cls=Player)
        ctx.voice_client._text_channel = ctx.channel

        embed = discord.Embed(colour=colours.MAIN, description=f'Joined voice channel `{ctx.voice_client.channel}`.')
        await ctx.send(embed=embed)

    @commands.command(name='disconnect', aliases=['dc', 'leave', 'destroy'])
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def disconnect(self, ctx: context.Context) -> None:
        """
        Disconnects the bot from the voice channel that it is in.
        """

        await ctx.send(embed=discord.Embed(colour=colours.MAIN, description=f'Left voice channel `{ctx.voice_client.channel}`.'))
        await ctx.voice_client.disconnect()

    @commands.command(name='pause')
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def pause(self, ctx: context.Context) -> None:
        """
        Pauses the current track.
        """

        if ctx.voice_client.paused:
            raise exceptions.VoiceError('The player is already paused.')

        await ctx.voice_client.set_pause(True)
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description='The player is now paused.'))

    @commands.command(name='resume', aliases=['continue', 'unpause'])
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def resume(self, ctx: context.Context) -> None:
        """
        Resumes the current track.
        """

        if ctx.voice_client.paused is False:
            raise exceptions.VoiceError('The player is not paused.')

        await ctx.voice_client.set_pause(False)
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description='The player is now resumed.'))

    @commands.command(name='seek')
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def seek(self, ctx: context.Context, *, time: converters.TimeConverter) -> None:
        """
        Seeks to a position on the current track.

        `seconds`: The position to seek too.
        """

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        # noinspection PyTypeChecker
        milliseconds = time * 1000

        if 0 < milliseconds > ctx.voice_client.current.length:
            raise exceptions.VoiceError(f'That was not a valid time, please choose a value between `0s` and `{utils.format_seconds(ctx.voice_client.current.length // 1000, friendly=True)}`.')

        await ctx.voice_client.set_position(milliseconds)
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description=f'The players position is now `{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}`.'))

    @commands.command(name='forward', aliases=['fwd'])
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def forward(self, ctx: context.Context, *, time: converters.TimeConverter) -> None:
        """
        Seeks forward a certain amount of time.

        `seconds`: The amount of time to seek forward.
        """

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        # noinspection PyTypeChecker
        milliseconds = time * 1000
        position = ctx.voice_client.position
        time_remaining = ctx.voice_client.current.length - position

        if milliseconds >= time_remaining:
            raise exceptions.VoiceError(f'That was not a valid amount of time. Please choose a value lower than `{utils.format_seconds(time_remaining // 1000, friendly=True)}`.')

        await ctx.voice_client.set_position(position + milliseconds)
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description=f'The players position is now `{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}`.'))

    @commands.command(name='rewind', aliases=['rwd'])
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def rewind(self, ctx: context.Context, *, time: converters.TimeConverter) -> None:
        """
        Seeks backward a certain amount of time.

        `seconds`: The amount of time to seek backward.
        """

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        # noinspection PyTypeChecker
        milliseconds = time * 1000
        position = ctx.voice_client.position

        if milliseconds >= ctx.voice_client.position:
            raise exceptions.VoiceError(f'That was not a valid amount of time. Please choose a value lower than `{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}`.')

        await ctx.voice_client.set_position(position - milliseconds)
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description=f'The players position is now `{utils.format_seconds(ctx.voice_client.position // 1000, friendly=True)}`.'))

    @commands.command(name='replay', aliases=['restart'])
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def replay(self, ctx: context.Context) -> None:
        """
        Seeks to the start of the current track.

        `seconds`: The position to seek too, in seconds.
        """

        if not ctx.voice_client.current.is_seekable:
            raise exceptions.VoiceError('The current track is not seekable.')

        await ctx.voice_client.set_position(position=0)
        await ctx.reply(f'The players position is now `{utils.format_seconds(seconds=0)}`.')

    @commands.command(name='skip', aliases=['voteskip', 'vote-skip', 'vote_skip'])
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def voteskip(self, ctx: context.Context) -> None:
        """
        Votes to skip the current track.
        """

        try:
            await commands.check_any(
                    commands.is_owner(), checks.is_guild_owner(), checks.is_track_requester(),
                    checks.has_any_permissions(manage_guild=True, kick_members=True, ban_members=True, manage_messages=True, manage_channels=True)
            ).predicate(ctx=ctx)

        except commands.CheckAnyFailure:

            if ctx.author not in ctx.voice_client.listeners:
                raise exceptions.VoiceError('You can not vote to skip as you are currently deafened.')

            if ctx.author.id in ctx.voice_client.skip_request_ids:
                ctx.voice_client.skip_request_ids.remove(ctx.author.id)
                message = 'Removed your vote to skip, '
            else:
                ctx.voice_client.skip_request_ids.add(ctx.author.id)
                message = 'Added your vote to skip, '

            skips_needed = (len(ctx.voice_client.listeners) // 2) + 1

            if len(ctx.voice_client.skip_request_ids) < skips_needed:
                await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description=f'{message} currently on `{len(ctx.voice_client.skip_request_ids)}` out of `{skips_needed}` votes needed to skip.'))
                return

        await ctx.voice_client.stop()
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description='Skipped the current track.'))

    @commands.command(name='forceskip', aliases=['force-skip', 'force_skip', 'fs'])
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def forceskip(self, ctx: context.Context) -> None:
        """
        Skips the current track.
        """

        try:
            await commands.check_any(
                    commands.is_owner(), checks.is_guild_owner(), checks.is_track_requester(),
                    checks.has_any_permissions(manage_guild=True, kick_members=True, ban_members=True, manage_messages=True, manage_channels=True)
            ).predicate(ctx=ctx)
        except commands.CheckAnyFailure:
            raise exceptions.VoiceError('You do not have permission to force skip.')

        await ctx.voice_client.stop()
        await ctx.reply(embed=discord.Embed(colour=colours.MAIN, description='Skipped the current track.'))

    @commands.command(name='loop', aliases=['loop-current', 'loop_current'])
    @checks.is_voice_client_playing()
    @checks.is_connected(same_channel=True)
    @checks.has_voice_client()
    async def loop(self, ctx: context.Context) -> None:
        """
        Loops the current track.
        """

        if ctx.voice_client.queue.is_looping_current:
            ctx.voice_client.queue.set_looping(looping=False)
            embed = discord.Embed(colour=colours.MAIN, description='The current track will stop looping.')
        else:
            ctx.voice_client.queue.set_looping(looping=True, current=True)
            embed = discord.Embed(colour=colours.MAIN, description='The current track will start looping.')

        await ctx.reply(embed=embed)


def setup(bot: Life) -> None:
    bot.add_cog(PlayerController(bot=bot))
