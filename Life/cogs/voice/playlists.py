from datetime import datetime

import discord
from discord.ext import commands

from cogs.voice import objects


class Playlists(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="playlist", aliases=["playlists"], invoke_without_command=True)
    async def playlist(self, ctx, *, search: str = None):

        playlists = await self.bot.db.fetch("SELECT * FROM playlists WHERE owner_id = $1", ctx.author.id)
        playlists = [objects.Playlist(dict(playlist)) for playlist in playlists]

        if not playlists:
            return await ctx.send("You have no playlists.")

        if search:
            playlists = [playlist for playlist in playlists if playlist.id == search or playlist.name == search]
            if not playlists:
                return await ctx.send(f"You have no playlists with the name or id: `{search}`")

        embeds = []

        for playlist in playlists:

            playlist_owner = self.bot.get_user(playlist.owner_id)
            embed = discord.Embed(
                colour=discord.Color.gold(),
                title=f"Playlist: {playlist.name}"
            )
            embed.set_footer(text=f"Playlist ID: {playlist.id} | Creation date: {playlist.creation_date}")
            embed.set_thumbnail(url=playlist_owner.avatar_url_as(format="png"))

            embed.add_field(name=f"Name:", value=f"{playlist.name}", inline=False)
            embed.add_field(name=f"Owner:", value=f"{playlist_owner.mention}")
            embed.add_field(name=f"Private:", value=f"{playlist.private}")
            # TODO get the first 10 or so tracks and add them here.

            embeds.append(embed)

        await ctx.paginate_embeds(entries=embeds)

    @playlist.command(name="create")
    async def playlist_create(self, ctx, *, name: str = None):
        """Create a playlist.

        `name`: The name of your new playlist. This can not be changed.
        """

        if not name:
            return await ctx.send("You must choose a name for you playlist.")

        await self.bot.db.execute("INSERT INTO playlists (name, owner_id, private, creation_date )values ($1, $2, $3, $4)", name, ctx.author.id, True, datetime.utcnow().strftime('%d-%m-%Y: %H:%M'))
        return await ctx.send(f"A playlist was created with the name `{name}`. Do `{ctx.prefix}playlist {name}` to view it.")

    @playlist.command(name="add")
    async def playlist_add(self, ctx, *, name: str, track: str):
        """Add a track to one of your playlists.

        `playlist`: The name of the playlist you want to add a track too.
        `track`: The name/link of the track you want to add.
        """

        playlist =True


def setup(bot):
    bot.add_cog(Playlists(bot))


