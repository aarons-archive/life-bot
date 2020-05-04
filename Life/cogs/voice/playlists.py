import asyncio
import typing
from datetime import datetime

import discord
import granitepy
import spotify
from discord.ext import commands

from cogs.utilities import exceptions, checks
from cogs.voice.utilities import objects


class Playlists(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_playlist_tracks(self, ctx: commands.Context, playlist: objects.Playlist):

        raw_tracks = await self.bot.db.fetch("SELECT * FROM playlist_tracks WHERE playlist_id = $1", playlist.id)
        if not raw_tracks:
            return

        for raw_track in raw_tracks:

            if raw_track.get("source") == "youtube":
                track = objects.GraniteTrack(track_id=raw_track.get("track_id"), info=raw_track, ctx=ctx)
            elif raw_track.get("source") == "spotify":
                track = objects.SpotifyTrack(ctx=ctx, title=raw_track.get("title"), author=raw_track.get("author"),
                                             length=raw_track.get("length"), uri=raw_track.get("uri"))
            else:
                continue

            playlist.tracks.append(track)

    async def get_playlists(self, ctx, owner: discord.Member = None, owned_by: bool = True, search: str = None):

        try:
            search = int(search)
        except ValueError:
            pass

        query = ['SELECT * FROM playlists ']
        query_data = []

        if type(search) == int:
            query.append('WHERE id = $1 ')
            query_data.append(search)

        elif type(search) == str:
            query.append('WHERE name = $1 ')
            query_data.append(search)

        if owner and owned_by is True:
            query.append(f'{"AND" if search else "WHERE"} owner_id = {"$2" if search else "$1"} ')
            query_data.append(owner.id)

        elif owner and owned_by is False:
            query.append(f'{"AND" if search else "WHERE"} owner_id != {"$2" if search else "$1"} AND private = $3')
            query_data.extend([owner.id, False])

        raw_playlists = await self.bot.db.fetch("".join(query), *query_data)
        if not raw_playlists:
            return None

        playlists = []
        for raw_playlist in raw_playlists:

            playlist = objects.Playlist(raw_playlist)
            await self.get_playlist_tracks(ctx=ctx, playlist=playlist)
            playlists.append(playlist)

        return playlists

    async def do_choice(self, ctx: commands.Context, message: str):

        await ctx.send(message)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            response = await self.bot.clean_content.convert(ctx, response.content)
        except asyncio.TimeoutError:
            raise exceptions.LifePlaylistError('You took too long to respond.')

        return response

    async def choose_playlist(self, ctx: commands.Context, playlists: list):

        if len(playlists) == 1:
            return playlists[0]

        message = '```py\n' \
                  'Your search returned more than one playlist, say the number of the playlist you want to use.\n\n'
        for index, playlist in enumerate(playlists):
            message += f'{index + 1}.  Name: {playlist.name} | ID: {playlist.id} | Tracks: ' \
                       f'{len(playlist.tracks)} | Owner: {self.bot.get_user(playlist.owner_id)}\n'
        message += '\n```'

        response = await self.do_choice(ctx=ctx, message=message)
        try:
            response = int(response) - 1
        except ValueError:
            raise exceptions.LifePlaylistError('You need to choose the number of the playlist to use.')

        if response < 0 or response >= len(playlists):
            raise exceptions.LifePlaylistError('That was not one of the available playlists.')

        return playlists[response]

    @commands.group(name='playlist', aliases=['playlists'], invoke_without_command=True)
    async def playlist(self, ctx, *, search: typing.Union[int, str] = None):
        pass

    @playlist.command(name='create', aliases=['make'])
    async def playlist_create(self, ctx, *, name: commands.clean_content):

        try:
            name = int(str(name))
            raise exceptions.LifePlaylistError('You can not use numbers in a playlist name.')
        except ValueError:
            pass
        if '`' in name:
            raise exceptions.LifePlaylistError('You can not use backtick characters in a playlist name.')

        query = 'INSERT INTO playlists (name, owner_id, private, creation_date, image_url) ' \
                'VALUES ($1, $2, $3, $4, $5) RETURNING *'
        image = self.bot.utils.member_avatar(ctx.author)
        raw_playlist = await self.bot.db.fetchrow(query, name, ctx.author.id, False, datetime.now(), image)
        playlist = objects.Playlist(raw_playlist)

        embed = discord.Embed(title='Playlist created', colour=discord.Colour.gold(),
                              description=f'**Name:** `{playlist.name}`\n**Private:** {playlist.private}\n'
                                          f'**Image:** [link]({playlist.image_url})')
        embed.set_footer(text=f'ID: {playlist.id} | Creation Date: {playlist.creation_date}')
        return await ctx.send(embed=embed)

    @playlist.command(name='delete')
    async def playlist_delete(self, ctx, *, playlist: commands.clean_content):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError(f'You have no playlists with the name or id: `{playlist}`')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        await self.bot.db.execute('DELETE FROM playlists WHERE id = $1', playlist.id)
        await self.bot.db.execute('DELETE FROM playlist_tracks WHERE playlist_id = $1', playlist.id)

        embed = discord.Embed(title='Playlist deleted', colour=discord.Colour.gold(),
                              description=f'**Name:** `{playlist.name}`\n**Private:** {playlist.private}\n'
                                          f'**Image:** [link]({playlist.image_url})')
        embed.set_footer(text=f'ID: {playlist.id} | Creation Date: {playlist.creation_date}')
        return await ctx.send(embed=embed)

    @playlist.command(name='edit')
    async def playlist_edit(self, ctx, *, playlist: commands.clean_content):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError(f'You have no playlists with the name or id: `{playlist}`')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        message = f'```py\n' \
                  f'Say the number of the atrribute you would like to edit about your playlist.\n\n' \
                  f'1. Name \n2. Image \n3. Private\n```'
        response = await self.do_choice(ctx=ctx, message=message)

        if response == '1':

            response = await self.do_choice(ctx=ctx, message='What would you like your new playlist to be called?')
            try:
                response = int(str(response))
                raise exceptions.LifePlaylistError('You can not use numbers in a playlist name.')
            except ValueError:
                pass
            if '`' in response:
                raise exceptions.LifePlaylistError('You can not use backtick characters in a playlist name.')

            query = f'UPDATE playlists SET name = $1 WHERE id = $2 RETURNING *'
            raw_playlist = await self.bot.db.fetchrow(query, response, playlist.id)
            new_playlist = objects.Playlist(raw_playlist)
            return await ctx.send(f'Your playlist `{playlist.name}` has been renamed to `{new_playlist.name}`.')

        elif response == '2':

            response = await self.do_choice(ctx=ctx, message='What would you the like your playlists image to be?')
            if self.bot.image_url_regex.match(response) is None:
                raise exceptions.LifePlaylistError('That was not a valid image url.')

            query = f'UPDATE playlists SET image_url = $1 WHERE id = $2 RETURNING *'
            raw_playlist = await self.bot.db.fetchrow(query, response, playlist.id)
            new_playlist = objects.Playlist(raw_playlist)
            return await ctx.send(f'Your playlists image has been changed from '
                                  f'**<{playlist.image_url}>** to **<{new_playlist.image_url}>**')

        elif response == '3':

            query = f'UPDATE playlists SET private = $1 WHERE id = $2 RETURNING *'
            raw_playlist = await self.bot.db.fetchrow(query, False if playlist.private is True else True, playlist.id)
            new_playlist = objects.Playlist(raw_playlist)
            return await ctx.send(f'Your playlists private status has been changed from '
                                  f'**{playlist.is_private}** to **{new_playlist.is_private}**.')

        else:
            raise exceptions.LifePlaylistError('You need to say the number of the attribute you want to edit.')

    @playlist.command(name='add')
    async def playlist_add(self, ctx, playlist: commands.clean_content, *, search: str):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError(f'You have no playlists with the name or id: `{playlist}`')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        async with ctx.channel.typing():

            search_result = await ctx.player.get_results(ctx=ctx, search=search)
            search_type = search_result.get('type')
            tracks = search_result.get('tracks')
            result = search_result.get('result')

            if search_type == 'spotify':

                if isinstance(result, spotify.Track):
                    message = f'Added the spotify track **{result.name}** to your playlist **{playlist.name}**.'
                elif isinstance(result, spotify.Album):
                    message = f'Added the spotify album **{result.name}** to your playlist **{playlist.name}** ' \
                              f'with a total of **{len(tracks)}** track(s).'
                elif isinstance(result, spotify.Playlist):
                    message = f'Added the spotify playlist **{result.name}** to your playlist **{playlist.name}** ' \
                              f'with a total of **{len(tracks)}** track(s).'

                entries = [(playlist.id, None, track.title, track.author, track.length, None, track.uri, False,
                            False, None, 'spotify') for track in tracks]

            elif search_type == 'youtube':

                if isinstance(result, granitepy.Playlist):
                    message = f'Added the youtube playlist **{result.name}** to your playlist **{playlist.name}** ' \
                              f'with a total of **{len(tracks)}** track(s).'
                elif isinstance(result[0], granitepy.Track):
                    message = f'Added the youtube track **{result[0].title}** to your playlist **{playlist.name}**.'
                    if result[0].is_stream:
                        return await ctx.send('I am unable to add youtube livestreams to playlists.')

                entries = [(playlist.id, track.track_id, track.title, track.author,
                            track.length, track.identifier, track.uri, track.is_stream,
                            track.is_seekable, track.position, 'youtube') for track in tracks]

            query = 'INSERT INTO playlist_tracks values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)'
            await self.bot.db.executemany(query, entries)

            return await ctx.send(message)

    @playlist.command(name='remove')
    async def playlist_remove(self, ctx, playlist: commands.clean_content, *, search: str):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=str(playlist))
        if not playlists:
            raise exceptions.LifePlaylistError(f'You have no playlists with the name or id: `{playlist}`')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        async with ctx.channel.typing():

            search_result = await ctx.player.get_results(ctx=ctx, search=search)
            search_type = search_result.get('type')
            tracks = search_result.get('tracks')
            result = search_result.get('result')

            if search_type == 'spotify':

                tracks_to_remove = [track for track in tracks if track.uri in playlist.uris]
                if not tracks_to_remove:
                    raise exceptions.LifePlaylistError(f'Your spotify search returned no tracks which '
                                                       f'could be removed from your playlist.')

                if isinstance(result, spotify.Track):
                    message = f'Removed the spotify track **{result.name}** from your playlist **{playlist.name}**.'
                elif isinstance(result, spotify.Album):
                    message = f'Removed all the tracks from the spotify album **{result.name}** from your playlist ' \
                              f'**{playlist.name}** with a total of **{len(tracks_to_remove)}** track(s) removed.'
                elif isinstance(result, spotify.Playlist):
                    message = f'Removed all the tracks from the spotify playlist **{result.name}** from your playlist '\
                              f'**{playlist.name}** with a total of **{len(tracks_to_remove)}** track(s) removed.'

            elif search_type == 'youtube':

                tracks_to_remove = [track for track in tracks if track.uri in playlist.uris]
                if not tracks_to_remove:
                    raise exceptions.LifePlaylistError(f'Your youtube search returned no tracks which '
                                                       f'could be removed from your playlist.')

                if isinstance(result, granitepy.Playlist):
                    message = f'Removed all the tracks from the youtube playlist ' \
                              f'**{result.name}** from your playlist **{playlist.name}**' \
                              f' with a total of **{len(tracks_to_remove)}** track(s) removed.'
                elif isinstance(result[0], granitepy.Track):
                    message = f'Removed the youtube track **{result[0].title}** ' \
                              f'from your playlist **{playlist.name}**.'

            query = 'DELETE FROM playlist_tracks WHERE playlist_id = $1 and uri = $2'
            entries = [(playlist.id, track.uri) for track in tracks_to_remove]
            await self.bot.db.executemany(query, entries)

            return await ctx.send(message)

    @playlist.command(name='queue', aliases=['play'])
    @checks.is_member_connected()
    async def playlist_queue(self, ctx, *, playlist: commands.clean_content):

        playlists = []

        owner_playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=str(playlist))
        if owner_playlists:
            playlists.extend(owner_playlists)

        other_playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, owned_by=False, search=str(playlist))
        if other_playlists:
            playlists.extend(other_playlists)

        if not playlists:
            raise exceptions.LifePlaylistError(f'There no public playlists with the name or id: `{playlist}`')

        playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)

        if not playlist.tracks:
            return await ctx.send(f'The playlist **{playlist.name}** has no tracks.')

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        await ctx.trigger_typing()

        ctx.player.queue.extend(playlist.tracks)
        return await ctx.send(f'Added the playlist **{playlist.name}** to the queue '
                              f'with a total of **{len(playlist.tracks)}** entries.')


def setup(bot):
    bot.add_cog(Playlists(bot))
