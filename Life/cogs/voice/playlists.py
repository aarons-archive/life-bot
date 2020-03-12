import json
from datetime import datetime

import discord
from discord.ext import commands
import typing

import granitepy
from cogs.voice import objects
from utilities import checks


class Playlists(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def fetch_playlists(self, ctx: commands.Context, owner: discord.Member = None, search: typing.Union[int, str] = None):

        raw_playlists = await self.bot.db.fetch("SELECT * FROM playlist")
        playlists = []

        for raw_playlist in raw_playlists:

            playlist = objects.Playlist(dict(raw_playlist))
            tracks = await self.bot.db.fetch("SELECT * FROM playlist_tracks WHERE playlist_id = $1", playlist.id)
            playlist.tracks = [objects.GraniteTrack(track["track_id"], json.loads(track["track_data"]), ctx) for track in tracks]
            playlists.append(playlist)

        if owner:
            playlists = [playlist for playlist in playlists if playlist.owner_id == ctx.author.id]

        if search:
            playlists = [playlist for playlist in playlists if playlist.id == search or playlist.name == search]

        return playlists

    async def add_to_playlist(self, playlist: objects.Playlist, tracks: list):
        entries = [(playlist.id, track.track_id, json.dumps(track.info)) for track in tracks]
        async with self.bot.db.acquire() as db:
            await db.copy_records_to_table(table_name="playlist_tracks", columns=("playlist_id", "track_id", "track_data"), records=entries)
        return len(entries)

    async def remove_from_playlist(self, playlist: objects.Playlist, tracks: list):
        entries = [(playlist.id, track.track_id) for track in tracks]
        async with self.bot.db.acquire() as db:
            await db.executemany("DELETE FROM playlist_tracks WHERE playlist_id = $1 and track_id = $2", entries)
        return len(entries)

    @commands.group(name="playlist", aliases=["playlists"], invoke_without_command=True)
    async def playlist(self, ctx, *, search: typing.Union[int, str] = None):

        playlists = await self.fetch_playlists(ctx=ctx, search=search)
        if not playlists:
            if search:
                return await ctx.send(f"You don't have any playlists with the name or id: `{search}`.")
            else:
                return await ctx.send(f"You don't have any playlists.")

        embeds = []

        for playlist in playlists:

            playlist_owner = self.bot.get_user(playlist.owner_id)
            embed = discord.Embed(
                colour=discord.Color.gold(),
                title=f"{playlist.name}"
            )
            embed.set_footer(text=f"Playlist ID: {playlist.id} | Creation date: {playlist.creation_date}")
            embed.set_thumbnail(url=playlist_owner.avatar_url_as(format="png"))

            embed.add_field(name=f"Name:", value=f"{playlist.name}", inline=False)
            embed.add_field(name=f"Owner:", value=f"{playlist_owner.mention}")
            embed.add_field(name=f"Private:", value=f"{playlist.private}")

            if playlist.tracks:
                embed.add_field(name="First 10 tracks:", value="\n".join([f"**[{track.title}]({track.uri})**" for track in playlist.tracks[:5]]), inline=False)

            embeds.append(embed)
            # TODO refactor this

        return await ctx.paginate_embeds(entries=embeds)

    @playlist.command(name="create")
    async def playlist_create(self, ctx, *, name: typing.Union[int, str] = None):

        if not name:
            return await ctx.send("You need to choose a name for your playlist.")

        if isinstance(name, int):
            return await ctx.send("You can not use a number as a name for your playlist.")

        query = "INSERT INTO playlist (name, owner_id, private, creation_date) VALUES ($1, $2, $3, $4)"
        await self.bot.db.execute(query, name, ctx.author.id, True, datetime.utcnow().strftime("%d-%m-%Y: %H:%M"))
        return await ctx.send(f"A playlist was created with the name `{name}`.")

    @playlist.command(name="delete")
    async def playlist_delete(self, ctx, *, name: typing.Union[int, str] = None):

        if not name:
            return await ctx.send("You need to specify the name or id of the playlist you want to delete.")

        playlists = await self.fetch_playlists(ctx=ctx, search=name)
        if not playlists:
            return await ctx.send(f"You don't have any playlists with the name or id: `{name}`")
        if len(playlists) > 1:
            return await ctx.send(f"Your search returned more than one playlist, try using the ID instead.")
        playlist = playlists[0]

        await self.bot.db.execute("DELETE FROM playlist WHERE id = $1", playlist.id)
        await self.bot.db.execute("DELETE FROM playlist_tracks WHERE playlist_id = $1", playlist.id)
        return await ctx.send(f"Your playlist with the name `{playlist.name}` was deleted.")

    @playlist.command(name="add")
    async def playlist_add(self, ctx, playlist: typing.Union[int, str], *, track: str):

        playlists = await self.fetch_playlists(ctx=ctx, search=playlist)
        if not playlists:
            return await ctx.send(f"You don't have any playlists with the name or id: `{playlist}`")
        if len(playlists) > 1:
            return await ctx.send(f"Your search returned more than one playlist, try using the ID instead.")
        playlist = playlists[0]

        await ctx.trigger_typing()

        result = await self.bot.granitepy.get_node().get_tracks(track)
        if not result:
            return await ctx.send(f"There were no tracks found for the search `{track}`.")

        if isinstance(result, granitepy.Playlist):
            yt_playlist = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)
            total_added = await self.add_to_playlist(playlist=playlist, tracks=yt_playlist.tracks)
            return await ctx.send(f"Added a total of **{total_added}** tracks from the playlist **{yt_playlist.name}** to your playlist **{playlist.name}**.")

        yt_track = objects.GraniteTrack(track_id=result[0].track_id, info=result[0].info, ctx=ctx)
        await self.add_to_playlist(playlist=playlist, tracks=[yt_track])
        return await ctx.send(f"Added the track **{yt_track.title}** to your playlist **{playlist.name}**.")

    @playlist.command(name="remove")
    async def playlist_remove(self, ctx, playlist: typing.Union[int, str], *, track: str):

        playlists = await self.fetch_playlists(ctx=ctx, search=playlist)
        if not playlists:
            return await ctx.send(f"You don't have any playlists with the name or id: `{playlist}`")
        if len(playlists) > 1:
            return await ctx.send(f"Your search returned more than one playlist, try using the ID instead.")
        playlist = playlists[0]

        await ctx.trigger_typing()

        result = await self.bot.granitepy.get_node().get_tracks(track)
        if not result:
            return await ctx.send(f"There were no tracks found for the search `{track}`.")

        if isinstance(result, granitepy.Playlist):
            yt_playlist = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)
            tracks_to_remove = [track for track in yt_playlist.tracks if track.track_id in playlist.track_ids]
            if not tracks_to_remove:
                return await ctx.send(f"There are no tracks in the youtube playlist **{yt_playlist.name}** that can be removed from your playlist **{playlist.name}**.")
            await self.remove_from_playlist(playlist=playlist, tracks=tracks_to_remove)
            return await ctx.send(f"Removed a total of **{len(tracks_to_remove)}** tracks from your playlist **{playlist.name}**.")

        yt_track = objects.GraniteTrack(track_id=result[0].track_id, info=result[0].info, ctx=ctx)
        if yt_track.track_id not in playlist.track_ids:
            return await ctx.send(f"The track **{yt_track.title}** is not in your playlist **{playlist.name}**.")
        await self.remove_from_playlist(playlist=playlist, tracks=[yt_track])
        return await ctx.send(f"Removed the track **{yt_track.title}** from your playlist **{playlist.name}**.")

    @playlist.command(name="queue")
    @checks.is_member_connected()
    async def playlist_queue(self, ctx, *, playlist: typing.Union[int, str]):

        playlists = await self.fetch_playlists(ctx=ctx, search=playlist)
        if not playlists:
            return await ctx.send(f"You don't have any playlists with the name or id: `{playlist}`")
        if len(playlists) > 1:
            return await ctx.send(f"Your search returned more than one playlist, try using the ID instead.")
        playlist = playlists[0]

        if not playlist.tracks:
            return await ctx.send(f"The playlist **{playlist.name}** has no tracks.")

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        await ctx.trigger_typing()

        for track in playlist.tracks:
            await ctx.player.queue.put(track)
        return await ctx.send(f"Added the playlist **{playlist.name}** to the queue with a total of **{len(playlist.tracks)}** entries.")


def setup(bot):
    bot.add_cog(Playlists(bot))
