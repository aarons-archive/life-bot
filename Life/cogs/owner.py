from discord.ext import commands
from youtube_dl import YoutubeDL
from .utils import botUtils
import discord
import asyncpg
import os

ytdlopts = {
    'format': 'bestaudio',
    'outtmpl': 'files/voice/%(id)s.%(ext)s',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors':
        [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
}
ytdl = YoutubeDL(ytdlopts)


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="download", hidden=True)
    async def download(self, ctx):
        """
        Downloads an mp3 version of the current track.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If nothing is current playing.
        if not ctx.player.current:
            return await ctx.send("No tracks currently playing.")

        # Start process
        message = await ctx.send("Downloading track... <a:downloading:616426925350715393>")
        await ctx.trigger_typing()

        # Download the track in an executor, cuz this is blocking.
        track_title, track_id = await self.bot.loop.run_in_executor(None, self.do_download, ctx)

        if ctx.guild.premium_tier == 1 or ctx.guild.premium_tier == 0:
            size = os.path.getsize(f"files/voice/{track_id}.mp3")
            if size >= 8388608:
                os.remove(f"files/voice/{track_id}.mp3")
                return await ctx.send("This track is too big to upload to discord.")
        if ctx.guild.premium_tier == 2:
            size = os.path.getsize(f"files/voice/{track_id}.mp3")
            if size >= 52428800:
                os.remove(f"files/voice/{track_id}.mp3")
                return await ctx.send("This track is too big to upload to discord.")
        if ctx.guild.premium_tier == 3:
            size = os.path.getsize(f"files/voice/{track_id}.mp3")
            if size >= 104857600:
                os.remove(f"files/voice/{track_id}.mp3")
                return await ctx.send("This track is too big to upload to discord.")

        await message.edit(content="Uploading track... <a:downloading:616426925350715393>")

        # Upload the file
        await ctx.send(content="Here is your download.", file=discord.File(filename=f"{track_title}.mp3", fp=f"files/voice/{track_id}.mp3"))

        # Delete the file and message
        os.remove(f"files/voice/{track_id}.mp3")
        return await message.delete()

    def do_download(self, ctx):
        data = ytdl.extract_info(f"{ctx.player.current.uri}", download=False)
        ytdl.download([f"{ctx.player.current.uri}"])
        return data["title"], data["id"]

    @commands.is_owner()
    @commands.command(name="stats", hidden=True)
    async def stats(self, ctx):
        """
        Show command usage/message stats.
        """

        # If no stats have been collected yet.
        if not self.bot.stats:
            return await ctx.send("No usage of commands yet.")

        # Define a list to store embeds in.
        embeds = []

        # Loop through bot.usage to get the guild and its command uses.
        for guild, usage in self.bot.stats.items():

            # Get the guild by its stored id.
            guild = self.bot.get_guild(guild)

            # Create the embed.
            embed = discord.Embed(
                title=f"{guild.name} ({guild.id})",
                description=f"",
                color=0xFF0000
            )
            for command in usage:
                embed.description += f"{command} : {usage[command]}\n"
            embeds.append(embed)

        # Send the message
        return await ctx.paginate_embeds(entries=embeds)

    @commands.is_owner()
    @commands.command(name="guilds", hidden=True)
    async def guilds(self, ctx):
        """
        Display information about all the different guilds the bot is in.
        """

        # Define a list for all the embeds.
        embeds = []

        # Loop through all bots guilds and create an embed for each one.
        for guild in self.bot.guilds:
            online, offline, idle, dnd = botUtils.guild_user_status_count(guild)
            embed = discord.Embed(
                colour=0xFF0000,
                title=f"{guild.name}'s Stats and Information."
            )
            embed.set_footer(text=f"ID: {guild.id}")
            embed.add_field(name="__**General information:**__", value=f"**Owner:** {guild.owner}\n"
                                                                       f"**Server created at:** {guild.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                       f"**Members:** {guild.member_count} |"
                                                                       f"<:online:627627415224713226>{online} |"
                                                                       f"<:away:627627415119724554>{idle} |"
                                                                       f"<:dnd:627627404784828416>{dnd} |"
                                                                       f"<:offline:627627415144890389>{offline}\n"
                                                                       f"**Verification level:** {botUtils.guild_verification_level(guild)}\n"
                                                                       f"**Content filter level:** {botUtils.guild_content_filter_level(guild)}\n"
                                                                       f"**2FA:** {botUtils.guild_mfa_level(guild)}\n"
                                                                       f"**Role Count:** {len(guild.roles)}\n", inline=False)
            embed.add_field(name="__**Channels:**__", value=f"**Text channels:** {len(guild.text_channels)}\n"
                                                            f"**Voice channels:** {len(guild.voice_channels)}\n"
                                                            f"**Voice region:** {botUtils.guild_region(guild)}\n"
                                                            f"**AFK timeout:** {int(guild.afk_timeout / 60)} minutes\n"
                                                            f"**AFK channel:** {guild.afk_channel}\n", inline=False)
            embed.set_thumbnail(url=guild.icon_url)

            # Append the embed to the list of embeds.
            embeds.append(embed)

        # Paginate the list of embeds.
        return await ctx.paginate_embeds(entries=embeds)

    @commands.is_owner()
    @commands.command(name="farms", hidden=True)
    async def farms(self, ctx, guilds_per_page=15):
        """
        Display how many bots/humans there are in each guild the bot can see.

        `guilds_per_page`: How many guilds to show per page, this is to reduce spam.
        """

        # Define a key to sort guilds by.
        def key(e):
            return sum([m.bot for m in e.members])

        # Define a list of entries to paginate through.
        entries = []

        # Set a title for the paginator.
        title = "Guild id           |Total    |Humans   |Bots     |Name\n"

        # Loop through all the guilds the bot can see.
        for guild in sorted(self.bot.guilds, key=key, reverse=True):

            # Count how many members are bot/humans.
            bots = sum(1 for m in guild.members if m.bot)
            humans = sum(1 for m in guild.members if not m.bot)
            total = len(guild.members)

            # Create a message with the current guilds information.
            message = f"{guild.id} |{total}{' ' * int(9 - len(str(total)))}|{humans}{' ' * int(9 - len(str(humans)))}|{bots}{' ' * int(9 - len(str(bots)))}|{guild.name}"

            # Append the message to the list of entries.
            entries.append(message)

        # Paginate the entries.
        return await ctx.paginate_codeblock(entries=entries, entries_per_page=guilds_per_page, title=title)

    @commands.is_owner()
    @commands.group(name="blacklist", hidden=True, invoke_without_command=True)
    async def blacklist(self, ctx):
        """
        Base command for blacklisting.
        """
        return await ctx.send("Please choose a valid subcommand.")

    @commands.is_owner()
    @blacklist.group(name="user", invoke_without_command=True)
    async def blacklist_user(self, ctx):
        """
        Display a list of all blacklisted users.
        """
        # Define a list for all blacklisted users.
        blacklisted = []

        # Fetch blacklisted users from the database.
        blacklist = await self.bot.db.fetch("SELECT * FROM user_blacklist")

        # If no blacklisted users where found, return.
        if not blacklist:
            return await ctx.send("No blacklisted users.")

        # Loop through users in the blacklist add them to the list of blacklisted users with their reason.
        for entry in blacklist:
            user = self.bot.get_user(entry['id'])
            if not user:
                blacklisted.append(f"User not found - {entry['id']} - Reason: {entry['reason']}")
            else:
                blacklisted.append(f"{user.name} - {user.id} - Reason: {entry['reason']}")

        # Paginate the list of blacklisted users.
        return await ctx.paginate_codeblock(entries=blacklisted, entries_per_page=10, title=f"Showing {len(blacklisted)} blacklisted users.\n\n")

    @commands.is_owner()
    @blacklist_user.command(name="add")
    async def blacklist_user_add(self, ctx, user: int = None, *, reason=None):
        """
        Add a user to the user blacklist.

        `user`: The users id.
        `reason`: Why the user is blacklisted.
        """
        # If the user doesnt specify a reason, add one.
        if not reason:
            reason = "No reason"

        # If the user picks a reason over 512 chars.
        if len(reason) > 512:
            return await ctx.caution("The reason can't be more than 512 characters.")

        # If the user doesn't specify a user to blacklist.
        if not user:
            return await ctx.send("You must specify a user id.")

        try:
            # Fetch the user and add them to the local blacklist and database.
            user = await self.bot.fetch_user(user)
            self.bot.guild_blacklist.append(user.id)
            await self.bot.db.execute("INSERT INTO user_blacklist (id, reason) VALUES ($1, $2)", user.id, reason)
            return await ctx.send(f"User: `{user.name} - {user.id}` has been blacklisted with reason `{reason}`")

        # Accept an error if the user is already blacklisted.
        except asyncpg.UniqueViolationError:
            return await ctx.send("That user is already blacklisted.")

    @commands.is_owner()
    @blacklist_user.command(name="remove")
    async def blacklist_user_remove(self, ctx, user: int = None):
        """
        Remove a user from the user blacklist.

        `user`: The users id.
        """

        # If the user doesn't specify a user to unblacklist.
        if not user:
            return await ctx.send("You must specify a user id.")
        try:
            # Fetch the user and remove them from the local blacklist and database.
            user = await self.bot.fetch_user(user)
            self.bot.guild_blacklist.remove(user.id)
            await self.bot.db.execute("DELETE FROM user_blacklist WHERE id = $1", user.id)
            return await ctx.send(f"User: `{user.name} - {user.id}` has been unblacklisted.")
        # Accept an error if the user is not blacklisted.
        except ValueError:
            return await ctx.send(f"User: `{user.name} - {user.id}` is not blacklisted.")

    @commands.is_owner()
    @blacklist.group(name="guild", invoke_without_command=True)
    async def blacklist_guild(self, ctx):
        """
        Display a list of all blacklisted guilds.
        """
        # Define a list of blacklisted guilds.
        blacklisted = []

        # Fetch blacklisted guilds from the database.
        blacklist = await self.bot.db.fetch("SELECT * FROM guild_blacklist")

        # If no guilds are blacklisted, return
        if not blacklist:
            return await ctx.send("No blacklisted guilds.")
        # Loop through blacklisted guilds and append to the list with their reason.
        for entry in blacklist:
            blacklisted.append(f"{entry['id']} - Reason: {entry['reason']}")

        # Paginate the list of blacklisted guilds.
        return await ctx.paginate_codeblock(entries=blacklisted, entries_per_page=10, title=f"Showing {len(blacklisted)} blacklisted guilds.\n\n")

    @commands.is_owner()
    @blacklist_guild.command(name="add")
    async def blacklist_guild_add(self, ctx, guild: int = None, *, reason=None):
        """
        Add a guild to the guild blacklist.

        `user`: The guilds id.
        `reason`: Why the guild is blacklisted.
        """
        # If the user doesnt specify a reason, add one.
        if not reason:
            reason = "No reason"

        # If the user picks a reason over 512 chars.
        if len(reason) > 512:
            return await ctx.caution("The reason can't be more than 512 characters.")

        # If the user doesn't specify a guild to blacklist.
        if not guild:
            return await ctx.send("You must specify a guild id.")

        try:
            # Add the guild to the local blacklist and database.
            self.bot.guild_blacklist.append(guild)
            await self.bot.db.execute("INSERT INTO guild_blacklist (id, reason) VALUES ($1, $2)", guild, reason)

            # Try to fetch the guild and leave it, accepting an error if we are not in the guild.
            try:
                guild = await self.bot.fetch_guild(guild)
                await guild.leave()
            except discord.Forbidden:
                pass

            return await ctx.send(f"Guild: `{guild}` has been blacklisted with reason `{reason}`")

        # Accept an error if the quild is already blacklisted.
        except asyncpg.UniqueViolationError:
            return await ctx.send("That guild is already blacklisted.")

    @commands.is_owner()
    @blacklist_guild.command(name="remove")
    async def blacklist_guild_remove(self, ctx, guild: int = None):
        """
        Remove a guild from the guild blacklist.

        `user`: The guilds id.
        """
        # If the user doesn't specify a guild to unblacklist.
        if not guild:
            return await ctx.send("You must specify a user id.")

        try:
            # Remove the guild from the local blacklist and database.
            self.bot.guild_blacklist.remove(guild)
            await self.bot.db.execute("DELETE FROM guild_blacklist WHERE id = $1", guild)
            return await ctx.send(f"Guild: `{guild}` has been unblacklisted.")
        # Accept an error if the guild is not blacklisted.
        except ValueError:
            return await ctx.send(f"Guild: `{guild}` is not blacklisted.")


def setup(bot):
    bot.add_cog(Owner(bot))
