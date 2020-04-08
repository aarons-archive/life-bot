import asyncio
import json
import typing
from datetime import datetime

import discord
from discord.ext import commands

import granitepy
from cogs.utilities import checks
from cogs.voice.utilities import objects


class Playlists(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_playlists(self, ctx, owner: discord.Member = None, search: typing.Union[int, str] = None):

        playlists = []
        raw_playlists = await self.bot.db.fetch("SELECT * FROM playlists")

        for raw_playlist in raw_playlists:

            playlist = objects.Playlist(dict(raw_playlist))

            # if the playlist is private and the author of this message is no the playlists owner then skip.
            if playlist.private is True and playlist.owner_id != ctx.author.id:
                continue

            # If we have the owner arg and the owner is not the playlists owner then skip.
            if owner is not None and owner.id != playlist.owner_id:
                continue

            # If the search is an int and the search is not equal to the playlists id then skip.
            if type(search) == int and search != playlist.id:
                continue

            # If the search is a str and the search is not equal to the playlists name then skip.
            if type(search) == str and search != playlist.name:
                continue

            tracks = await self.bot.db.fetch("SELECT * FROM playlist_tracks WHERE playlist_id = $1", playlist.id)
            playlist.tracks = [objects.GraniteTrack(track["track_id"], json.loads(track["track_data"]), ctx) for track in tracks]
            playlists.append(playlist)

        return playlists

    async def choose_playlist(self, ctx, playlists: list):

        message = "```py\nYour search returned more than one playlist, say the number of the playlist you want to use.\n\n"
        for index, playlist in enumerate(playlists):
            owner = self.bot.get_user(playlist.owner_id)
            message += f"{index + 1}.  Name: {playlist.name} | ID: {playlist.id} | Tracks: {len(playlist.tracks)} | Owner: {owner}\n"
        message += "\n```"
        await ctx.send(message)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
            response = int(response.content) - 1
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            return None
        except ValueError:
            await ctx.send("You need to choose the number of the playlist to use.")
            return None

        if response < 0 or response >= len(playlists):
            await ctx.send("That wasn't one of the available playlists.")
            return None

        playlist = playlists[response]
        return playlist

    @commands.group(name="playlist", invoke_without_command=True)
    async def playlist(self, ctx, *, search: typing.Union[int, str] = None):
        pass

    @playlist.command(name="create")
    async def playlist_create(self, ctx, *, name: typing.Union[int, commands.clean_content]):

        if isinstance(name, int):
            return await ctx.send("You can not use a number as a name for your playlist.")

        query = "INSERT INTO playlists (name, owner_id, private, creation_date, image_url) VALUES ($1, $2, $3, $4, $5)"
        await self.bot.db.execute(query, name, ctx.author.id, False, datetime.utcnow().strftime("%d-%m-%Y: %H:%M"), self.bot.utils.member_avatar(ctx.author))
        return await ctx.send(f"Playlist `{name}` was successfully created.")

    @playlist.command(name="delete")
    async def playlist_delete(self, ctx, *, playlist: typing.Union[int, commands.clean_content]):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=playlist)
        if not playlists:
            return await ctx.send(f"No playlists were found with the name or id: `{playlist}`")

        playlist = playlists[0]
        if len(playlists) > 1:
            playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)
            if playlist is None:
                return

        await self.bot.db.execute("DELETE FROM playlists WHERE id = $1", playlist.id)
        await self.bot.db.execute("DELETE FROM playlist_tracks WHERE playlist_id = $1", playlist.id)
        return await ctx.send(f"Playlist `{playlist.name}` with id `{playlist.id}` was deleted.")

    @playlist.command(name="add")
    async def playlist_add(self, ctx, playlist: typing.Union[int, commands.clean_content], *, track: str):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=playlist)
        if not playlists:
            return await ctx.send(f"No playlists were found with the name or id: `{playlist}`")

        playlist = playlists[0]
        if len(playlists) > 1:
            playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)
            if playlist is None:
                return

        async with ctx.channel.typing():

            result = await self.bot.granitepy.get_node().get_tracks(track)
            if not result:
                return await ctx.send(f"There were no tracks found for the search `{track}`.")

            if isinstance(result, granitepy.Playlist):

                yt_playlist = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)

                entries = [(playlist.id, track.track_id, json.dumps(track.info)) for track in yt_playlist.tracks]
                async with self.bot.db.acquire() as db:
                    await db.copy_records_to_table(table_name="playlist_tracks", columns=("playlist_id", "track_id", "track_data"), records=entries)

                return await ctx.send(f"Added a total of **{len(entries)}** tracks from the playlist **{yt_playlist.name}** to your playlist **{playlist.name}**.")

            yt_track = objects.GraniteTrack(track_id=result[0].track_id, info=result[0].info, ctx=ctx)

            entries = [(playlist.id, yt_track.track_id, json.dumps(yt_track.info))]
            async with self.bot.db.acquire() as db:
                await db.copy_records_to_table(table_name="playlist_tracks", columns=("playlist_id", "track_id", "track_data"), records=entries)

            return await ctx.send(f"Added the track **{yt_track.title}** to your playlist **{playlist.name}**.")

    @playlist.command(name="remove")
    async def playlist_remove(self, ctx, playlist: typing.Union[int, commands.clean_content], *, track: str):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=playlist)
        if not playlists:
            return await ctx.send(f"No playlists were found with the name or id: `{playlist}`")

        playlist = playlists[0]
        if len(playlists) > 1:
            playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)
            if playlist is None:
                return

        async with ctx.channel.typing():

            result = await self.bot.granitepy.get_node().get_tracks(track)
            if not result:
                return await ctx.send(f"There were no tracks found for the search `{track}`.")

            if isinstance(result, granitepy.Playlist):

                yt_playlist = objects.GranitePlaylist(playlist_info=result.playlist_info, tracks=result.tracks_raw, ctx=ctx)

                tracks_to_remove = [track for track in yt_playlist.tracks if track.track_id in playlist.track_ids]
                if not tracks_to_remove:
                    return await ctx.send(f"There are no tracks in the youtube playlist **{yt_playlist.name}** that can be removed from your playlist **{playlist.name}**.")

                entries = [(playlist.id, track.track_id) for track in tracks_to_remove]
                async with self.bot.db.acquire() as db:
                    await db.executemany("DELETE FROM playlist_tracks WHERE playlist_id = $1 and track_id = $2", entries)

                return await ctx.send(f"Removed a total of **{len(entries)}** tracks from your playlist **{playlist.name}**.")

            yt_track = objects.GraniteTrack(track_id=result[0].track_id, info=result[0].info, ctx=ctx)
            if yt_track.track_id not in playlist.track_ids:
                return await ctx.send(f"The track **{yt_track.title}** is not in your playlist **{playlist.name}**.")

            async with self.bot.db.acquire() as db:
                await db.execute("DELETE FROM playlist_tracks WHERE playlist_id = $1 and track_id = $2", playlist.id, yt_track.track_id)

            return await ctx.send(f"Removed the track **{yt_track.title}** from your playlist **{playlist.name}**.")

    @playlist.command(name="queue", aliases=["play"])
    @checks.is_member_connected()
    async def playlist_queue(self, ctx, *, playlist: typing.Union[int, str]):

        playlists = await self.get_playlists(ctx=ctx, owner=ctx.author, search=playlist)
        if not playlists:
            playlists = await self.get_playlists(ctx=ctx, search=playlist)
            if not playlists:
                await ctx.send(f"No playlists were found with the name or id: `{playlist}`")

        playlist = playlists[0]
        if len(playlists) > 1:
            playlist = await self.choose_playlist(ctx=ctx, playlists=playlists)
            if playlist is None:
                return

        if not playlist.tracks:
            return await ctx.send(f"The playlist **{playlist.name}** has no tracks.")

        if not ctx.player.is_connected:
            ctx.player.text_channel = ctx.channel
            await ctx.player.connect(ctx.author.voice.channel)

        await ctx.trigger_typing()

        ctx.player.queue.extend(playlist.tracks)
        return await ctx.send(f"Added the playlist **{playlist.name}** to the queue with a total of **{len(playlist.tracks)}** entries.")


def setup(bot):
    bot.add_cog(Playlists(bot))
