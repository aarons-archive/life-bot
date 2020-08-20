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

import spotify
from discord.ext import commands

from bot import Life
from utilities import context, exceptions
from cogs.voice.lavalink import client, objects
from cogs.voice.lavalink.exceptions import *


class Music(commands.Cog):

    def __init__(self, bot: Life):
        self.bot = bot

        self.bot.lavalink = client.Client(bot=self.bot, session=self.bot.session)
        self.bot.spotify = spotify.Client(client_id=self.bot.config.spotify_app_id, client_secret=self.bot.config.spotify_secret)
        self.bot.spotify_http = spotify.HTTPClient(client_id=self.bot.config.spotify_app_id, client_secret=self.bot.config.spotify_secret)

        self.load_task = asyncio.create_task(self.load())

    async def load(self):

        for node in self.bot.config.nodes:
            try:
                await self.bot.lavalink.create_node(host=node['host'], port=node['port'], password=node['password'], identifier=node['identifier'])
            except NodeCreationError as e:
                print(f'[LAVALINK] {e}')
            else:
                print(f'[LAVALINK] Node {node["identifier"]} connected.')

    @commands.Cog.listener()
    async def on_lavalink_track_start(self, event: objects.TrackStartEvent):
        await event.player.invoke_controller()
        event.player.wait_track_start.set()

    @commands.Cog.listener()
    async def on_lavalink_track_end(self, event: objects.TrackEndEvent):
        event.player.wait_track_end.set()

    @commands.Cog.listener()
    async def on_lavalink_track_exception(self, event: objects.TrackExceptionEvent):
        await event.player.send(message=f'Something went wrong while playing the track `{event.track.title}`. Error: `{event.error}`')
        event.player.wait_track_end.set()

    @commands.Cog.listener()
    async def on_lavalink_track_stuck(self, event: objects.TrackStuckEvent):
        await event.player.send(message=f'Something went wrong while playing the track `{event.track.title}`.')
        event.player.wait_track_end.set()

    @commands.Cog.listener()
    async def on_lavalink_websocket_closed(self, event: objects.WebSocketClosedEvent):
        pass

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx: context.Context):
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

        return await ctx.send(f'Joined your voice channel `{channel}`.')

    @commands.command(name='play')
    async def play(self, ctx: context.Context, *, query: str):
        """
        Plays/queues a track with the given search. Supports spotify.

        `query`: The name/link of the track you want to play. Spotify links will search youtube with the track name.
        """

        if not ctx.guild.voice_client or not ctx.guild.voice_client.is_connected:
            await ctx.invoke(self.join)

        channel = getattr(ctx.author.voice, 'channel', None)
        if not channel or channel.id != ctx.guild.voice_client.channel.id:
            raise exceptions.VoiceError(f'You must be connected to the same voice channel as me to use this command.')

        async with ctx.channel.typing():

            search = await ctx.guild.voice_client.node.search(query=query, ctx=ctx)

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

            ctx.guild.voice_client.queue.extend(items=tracks)
            return await ctx.send(message)


def setup(bot):
    bot.add_cog(Music(bot))
