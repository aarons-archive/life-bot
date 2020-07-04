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
from datetime import datetime
from typing import List, Union

import discord
from discord.ext import commands

from cogs.utilities import exceptions
from cogs.voice.utilities import objects


class Playlists(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_playlist_tracks(self, ctx, playlist: objects.Playlist) -> \
            List[Union[objects.SpotifyTrack, objects.LifeTrack]]:

        raw_tracks = await self.bot.db.fetch('SELECT * FROM playlist_tracks WHERE playlist_id = $1', playlist.id)
        tracks = []

        for raw_track in raw_tracks:
            if raw_track.get('source') == 'spotify':
                track = objects.SpotifyTrack(info=raw_track, ctx=ctx)
            else:
                track = objects.LifeTrack(track_id=raw_track.get('track_id'), info=raw_track, ctx=ctx)

            tracks.append(track)

        return tracks

    async def get_playlists_owned_by(self, ctx, owner: discord.Member, search: Union[int, str] = None) -> \
            List[objects.Playlist]:

        query = ['SELECT * FROM playlists WHERE owner_id = $1 ']
        query_data = [owner.id]

        if search:
            search = self.bot.utils.try_int(search)
            if type(search) == int:
                query.append('AND id = $2 ORDER BY creation_date DESC LIMIT 10')
                query_data.append(search)
            if type(search) == str:
                query.append('ORDER BY SIMILARITY(name, $2) DESC, creation_date DESC LIMIT 10')
                query_data.append(search)
        else:
            query.append('ORDER BY creation_date DESC LIMIT 10')

        raw_playlists = await self.bot.db.fetch(''.join(query), *query_data)
        playlists = [objects.Playlist(raw_playlist) for raw_playlist in raw_playlists]
        playlist_names = [playlist.name for playlist in playlists]

        for playlist in playlists:
            tracks = await self.get_playlist_tracks(ctx=ctx, playlist=playlist)
            playlist.tracks.extend(tracks)

            if playlist.name == search and playlist_names.count(playlist.name) == 1:
                return [playlist]

        return playlists

    async def get_playlists_not_owned_by(self, ctx, owner: discord.Member, search: Union[int, str] = None) -> \
            List[objects.Playlist]:

        query = ['SELECT * FROM playlists WHERE owner_id != $1 and private = $2 ']
        query_data = [owner.id, False]

        if search:
            search = self.bot.utils.try_int(search)
            if type(search) == int:
                query.append('AND id = $3 ORDER BY creation_date DESC LIMIT 10')
                query_data.append(search)
            if type(search) == str:
                query.append('ORDER BY SIMILARITY(name, $3) DESC, creation_date DESC LIMIT 10')
                query_data.append(search)
        else:
            query.append('ORDER BY creation_date DESC LIMIT 10')

        raw_playlists = await self.bot.db.fetch(''.join(query), *query_data)
        playlists = [objects.Playlist(raw_playlist) for raw_playlist in raw_playlists]
        playlist_names = [playlist.name for playlist in playlists]

        for playlist in playlists:
            tracks = await self.get_playlist_tracks(ctx=ctx, playlist=playlist)
            playlist.tracks.extend(tracks)

            if playlist.name == search and playlist_names.count(playlist.name) == 1:
                return [playlist]

        return playlists

    async def do_choice(self, ctx: commands.Context, message: str) -> str:

        await ctx.send(message)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            raise exceptions.LifePlaylistError('You took too long to respond.')
        else:
            response = await self.bot.clean_content.convert(ctx, response.content)

        return response

    async def choose_playlist(self, ctx, playlists: List[objects.Playlist]) -> objects.Playlist:

        if len(playlists) == 1:
            return playlists[0]

        message = [' ```py\nSay the number of the playlist you want to use.\n\n']
        for index, playlist in enumerate(playlists):
            message.append(f'{index + 1:<3} |Name: {playlist.name:<15} |ID: {playlist.id:<5} |'
                           f'Tracks: {len(playlist.tracks):<5} |Owner: {self.bot.get_user(playlist.owner_id)}\n')
        message.append('\n```')

        response = await self.do_choice(ctx=ctx, message=''.join(message))
        try:
            response = int(response) - 1
        except ValueError:
            raise exceptions.LifePlaylistError('That was not a valid number.')

        if response < 0 or response >= len(playlists):
            raise exceptions.LifePlaylistError('That was not one of the available playlists.')

        return playlists[response]

    @commands.group(name='playlist', aliases=['playlists', 'pl'], invoke_without_command=True)
    async def playlist(self, ctx):
        return await ctx.send(f'Please choose a valid subcommand. Use `{self.bot.config.prefix}help playlists` for '
                              f'more information.')

    @playlist.command(name='list')
    async def playlist_list(self, ctx, *, search: commands.clean_content = None):
        playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(search) if search else None)
        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        await ctx.paginate(entries=playlists, entries_per_page=20)  # TODO make this shit prettier i guess.

    @playlist.command(name='view')
    async def playlist_view(self, ctx, *, search: commands.clean_content):

        playlists = []

        owner_playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(search))
        if owner_playlists:
            playlists.extend(owner_playlists)

        other_playlists = await self.get_playlists_not_owned_by(ctx=ctx, owner=ctx.author, search=str(search))
        if other_playlists:
            playlists.extend(other_playlists)

        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        embed = discord.Embed(title=f'{playlist.name}', colour=discord.Colour.gold(),
                              description=f'**Private:** {playlist.private}\n'
                                          f'**ID:** {playlist.id}')
        embed.set_footer(text=f'Creation Date: {playlist.creation_date}')
        return await ctx.send(embed=embed)

    @playlist.command(name='create', aliases=['make'])
    async def playlist_create(self, ctx, *, name: commands.clean_content):

        count = await self.bot.db.fetchrow('SELECT count(*) as c FROM playlists WHERE owner_id = $1', ctx.author.id)
        if count['c'] >= 30:
            raise exceptions.LifePlaylistError('You can only have a maximum of 30 playlists.')

        name = self.bot.utils.try_int(string=str(name))
        if type(name) == int:
            raise exceptions.LifePlaylistError('You can not use only numbers as a playlist name.')
        if len(name) > 15:
            raise exceptions.LifePlaylistError('You can not have more than 15 characters in your playlist name.')
        if '`' in name:
            raise exceptions.LifePlaylistError('You can not use backticks in a playlist name.')

        query = 'INSERT INTO playlists (name, owner_id, private, creation_date) VALUES ($1, $2, $3, $4) RETURNING *'
        playlist = objects.Playlist(await self.bot.db.fetchrow(query, name, ctx.author.id, False, datetime.now()))

        embed = discord.Embed(title='Playlist created', colour=discord.Colour.gold(),
                              description=f'**Name:** `{playlist.name}`\n**Private:** {playlist.private}\n'
                                          f'**ID:** {playlist.id}')
        embed.set_footer(text=f'Creation Date: {playlist.creation_date}')
        return await ctx.send(embed=embed)

    @playlist.command(name='delete')
    async def playlist_delete(self, ctx, *, playlist: commands.clean_content):

        playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        await self.bot.db.execute('DELETE FROM playlists WHERE id = $1', playlist.id)
        await self.bot.db.execute('DELETE FROM playlist_tracks WHERE playlist_id = $1', playlist.id)

        embed = discord.Embed(title='Playlist deleted', colour=discord.Colour.gold(),
                              description=f'**Name:** `{playlist.name}`\n**Private:** {playlist.private}\n'
                                          f'**ID:** {playlist.id}')
        embed.set_footer(text=f'Creation Date: {playlist.creation_date}')
        return await ctx.send(embed=embed)

    @playlist.command(name='edit')
    async def playlist_edit(self, ctx, *, playlist: commands.clean_content):

        playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        message = f'```py\nSay the number of the atrribute you would like to edit about your playlist.\n\n' \
                  f'1. Name \n2. Private\n```'
        response = await self.do_choice(ctx=ctx, message=message)

        if response == '1':

            new_name = await self.do_choice(ctx=ctx, message='What would you like to rename your playlist too?')
            new_name = self.bot.utils.try_int(string=new_name)
            if type(new_name) == int:
                raise exceptions.LifePlaylistError('You can not use only numbers as a playlist name.')
            if len(new_name) > 15:
                raise exceptions.LifePlaylistError('You can not have more than 15 characters in your playlist name.')
            if '`' in new_name:
                raise exceptions.LifePlaylistError('You can not use backticks in a playlist name.')

            query = f'UPDATE playlists SET name = $1 WHERE id = $2 RETURNING *'
            raw_playlist = await self.bot.db.fetchrow(query, new_name, playlist.id)
            new_playlist = objects.Playlist(raw_playlist)
            return await ctx.send(f'Your playlist `{playlist.name}` has been renamed to `{new_playlist.name}`.')

        if response == '2':

            query = f'UPDATE playlists SET private = $1 WHERE id = $2 RETURNING *'
            raw_playlist = await self.bot.db.fetchrow(query, False if playlist.private is True else True, playlist.id)
            new_playlist = objects.Playlist(raw_playlist)
            return await ctx.send(f'Your playlists private status has been changed from `{playlist.is_private}` to '
                                  f'`{new_playlist.is_private}`.')

        else:
            raise exceptions.LifePlaylistError('That was not a valid attribute.')

    @playlist.command(name='add')
    async def playlist_add(self, ctx, playlist: commands.clean_content, *, query: str):

        playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        async with ctx.channel.typing():

            search = await ctx.player.search(ctx=ctx, search=query)

            if search.source == 'spotify':

                if search.source_type == 'track':
                    message = f'Added the spotify track **{search.result.name}** to your playlist **{playlist.name}**.'
                elif search.source_type in ('album', 'playlist'):
                    message = f'Added the spotify {search.source_type} **{search.result.name}** to your playlist ' \
                              f'**{playlist.name}** with a total of **{len(search.tracks)}** track(s).'

                entries = [(playlist.id, None, track.title, track.author, track.length, track.identifier, track.uri,
                            False, True, 0, 'spotify', track.thumbnail) for track in search.tracks]

                query = 'INSERT INTO playlist_tracks values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)'
                await self.bot.db.executemany(query, entries)

                return await ctx.send(message)

            elif search.source == 'youtube':

                if search.source_type == 'playlist':
                    message = f'Added the youtube playlist **{search.result.name}** to your playlist ' \
                              f'**{playlist.name}** with a total of **{len(search.tracks)}** track(s).'
                    tracks = search.tracks
                elif search.source_type == 'track':
                    if search.result[0].is_stream:
                        raise exceptions.LifePlaylistError('I am unable to add youtube livestreams to playlists.')
                    message = f'Added the youtube track **{search.result[0].title}** to your playlist ' \
                              f'**{playlist.name}**.'
                    tracks = [search.tracks[0]]

                entries = [(playlist.id, track.track_id, track.title, track.author, track.length, track.identifier,
                            track.uri, track.is_stream, track.is_seekable, track.position, track.thumbnail, 'youtube')
                           for track in tracks]

                query = 'INSERT INTO playlist_tracks values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)'
                await self.bot.db.executemany(query, entries)

                return await ctx.send(message)

    @playlist.command(name='remove')
    async def playlist_remove(self, ctx, playlist: commands.clean_content, *, search: str):

        playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        async with ctx.channel.typing():

            search = await ctx.player.search(ctx=ctx, search=search)

            if search.source == 'spotify':

                tracks_to_remove = [track for track in search.tracks if track.uri in [t.uri for t in playlist.tracks]]
                if not tracks_to_remove:
                    raise exceptions.LifePlaylistError(f'Your spotify search returned no tracks which could be removed '
                                                       f'from the playlist `{playlist.name}`.')

                if search.source_type == 'track':
                    message = f'Removed the spotify track **{search.result.name}** from your playlist ' \
                              f'**{playlist.name}**.'
                elif search.source_type in ('album', 'playlist'):
                    message = f'Removed all the tracks from the spotify {search.source_type} **{search.result.name}** '\
                              f'from your playlist **{playlist.name}**.'

            elif search.source == 'youtube':

                tracks_to_remove = [track for track in search.tracks if track.uri in [t.uri for t in playlist.tracks]]
                if not tracks_to_remove:
                    raise exceptions.LifePlaylistError(f'Your youtube search returned no tracks which could be removed '
                                                       f'from the playlist `{playlist.name}`.')

                if search.source_type == 'playlist':
                    message = f'Removed all the tracks from the youtube playlist **{search.result.name}** from your ' \
                              f'playlist **{playlist.name}**'
                elif search.source_type == 'track':
                    message = f'Removed the youtube track **{search.result[0].title}** from your playlist ' \
                              f'**{playlist.name}**.'

            entries = [(playlist.id, track.uri) for track in tracks_to_remove]
            await self.bot.db.executemany('DELETE FROM playlist_tracks WHERE playlist_id = $1 and uri = $2', entries)

            return await ctx.send(message)

    @playlist.command(name='queue', aliases=['play'])
    async def playlist_queue(self, ctx, *, playlist: commands.clean_content):

        playlists = []

        owner_playlists = await self.get_playlists_owned_by(ctx=ctx, owner=ctx.author, search=str(playlist))
        if owner_playlists:
            playlists.extend(owner_playlists)

        other_playlists = await self.get_playlists_not_owned_by(ctx=ctx, owner=ctx.author, search=str(playlist))
        if other_playlists:
            playlists.extend(other_playlists)

        if not playlists:
            raise exceptions.LifePlaylistError('You do not have any playlists.')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        if not playlist.tracks:
            return await ctx.send(f'The playlist **{playlist.name}** has no tracks.')

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        if ctx.author.voice.channel != ctx.player.voice_channel:
            raise commands.CheckFailure(f'You are not connected to the same voice channel as me.')

        ctx.player.queue.extend(playlist.tracks)
        return await ctx.send(f'Added the playlist **{playlist.name}** to the queue with a total of '
                              f'**{len(playlist.tracks)}** entries.')


def setup(bot):
    bot.add_cog(Playlists(bot))
