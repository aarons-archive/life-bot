import collections
import time

import asyncpg
import discord
from discord.ext import commands

from .utilities import imaging
from .utilities import utils


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.socket_stats = collections.Counter()

    @commands.is_owner()
    @commands.command(name="usage", hidden=True)
    async def usage(self, ctx, display: str = None):
        """
        Show command usage/message stats.
        """

        # If no stats have been collected yet.
        if not self.bot.usage:
            return await ctx.send("No usage of commands yet.")

        # Get the total usage of all commands in all guilds.
        total_usage = {}
        for guild_usage in self.bot.usage.values():
            for command, usage in guild_usage.items():
                if command not in total_usage:
                    total_usage[command] = usage
                else:
                    total_usage[command] += usage
        total_usage = collections.OrderedDict(sorted(total_usage.items(), key=lambda kv: kv[1], reverse=True))

        # If the user doesnt want a pie/bar chart.
        if display is None:

            # Define a list to store embeds in.
            embeds = []
            # Add a total usage embed.
            embed = discord.Embed(
                colour=discord.Color.gold(),
                title=f"Total usage",
                description=f"```py\n"
            )
            embed.set_thumbnail(url=self.bot.user.avatar_url_as(format="png", size=1024))
            for command, usage in total_usage.items():
                embed.description += f"{command} : {usage}\n"
            embed.description += "```"
            embeds.append(embed)

            # Loop through all the guilds in the bots usage to get the guild and its command uses.
            for guild_id, guild_usage in self.bot.usage.items():
                # Get the guild by its stored id.
                guild = self.bot.get_guild(guild_id)
                # If the guild is not found anymore, skip it.
                if guild is None:
                    continue
                usage = collections.OrderedDict(sorted(guild_usage.items(), key=lambda kv: kv[1], reverse=True))
                # Create the embed.
                embed = discord.Embed(
                    colour=discord.Color.gold(),
                    title=f"{guild.name}",
                    description=f"```py\n"
                )
                embed.set_footer(text=f"{guild.id}")
                embed.set_thumbnail(url=guild.icon_url_as(format="png", size=1024))
                for command, command_usage in usage.items():
                    embed.description += f"{command} : {command_usage}\n"
                embed.description += "```"
                # Append the embed to the list of embeds
                embeds.append(embed)
            # Send the message
            return await ctx.paginate_embeds(entries=embeds)

        # Generate a pie chart.
        if display in ["pie", "piechart"]:

            # Start timer.
            start = time.perf_counter()
            # Create the image and send it.
            pie_chart = imaging.do_pie_chart([v for v in total_usage.values()], [k for k in total_usage.keys()])
            await ctx.send(file=discord.File(filename=f"StatsPie.png", fp=pie_chart))
            # End timer and log how long operation took.
            end = time.perf_counter()
            return await ctx.send(f"That took {end - start:.3f}sec to complete")

        # Generate a bar chart.
        if display in ["bar", "barchart"]:

            # Start timer.
            start = time.perf_counter()
            # Create the image and send it.
            bar_chart = imaging.do_bar_chart("Command usage", "Command", "Usage", [v for v in total_usage.values()], [k for k in total_usage.keys()])
            await ctx.send(file=discord.File(filename=f"StatsBar.png", fp=bar_chart))
            # End timer and log how long operation took.
            end = time.perf_counter()
            return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.is_owner()
    @commands.command(name="user_growth", aliases=["ug"], hidden=True)
    async def user_growth(self, ctx, history: int = None):

        if history is None:
            history = 15

        user_growth = await self.bot.db.fetch("WITH t AS (SELECT * from bot_growth ORDER BY date DESC LIMIT $1) SELECT * FROM t ORDER BY date", history)

        # Start timer.
        start = time.perf_counter()
        # Create the image and send it.
        plot = imaging.do_plot("User growth", "Datetime", "Users", [record["member_count"] for record in user_growth], [record["date"] for record in user_growth])
        await ctx.send(file=discord.File(filename=f"UserGrowth.png", fp=plot))
        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

    @commands.is_owner()
    @commands.command(name="guild_growth", aliases=["gg"], hidden=True)
    async def guild_growth(self, ctx, history: int = None):

        if history is None:
            history = 15

        guild_growth = await self.bot.db.fetch("WITH t AS (SELECT * from bot_growth ORDER BY date DESC LIMIT $1) SELECT * FROM t ORDER BY date", history)

        # Start timer.
        start = time.perf_counter()
        # Create the image and send it.
        plot = imaging.do_plot("Guild growth", "Datetime", "Guilds", [record["guild_count"] for record in guild_growth], [record["date"] for record in guild_growth])
        await ctx.send(file=discord.File(filename=f"GuildGrowth.png", fp=plot))
        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")

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
            online, idle, dnd, offline = utils.guild_user_status(guild)
            embed = discord.Embed(
                colour=discord.Color.gold(),
                title=f"{guild.name}'s Stats and Information."
            )
            embed.set_thumbnail(url=guild.icon_url)
            embed.set_footer(text=f"ID: {guild.id}")
            embed.add_field(name="__**General information:**__", value=f"**Owner:** {guild.owner}\n"
                                                                       f"**Server created at:** {guild.created_at.__format__('%A %d %B %Y at %H:%M')}\n"
                                                                       f"**Members:** {guild.member_count} |"
                                                                       f"<:online:627627415224713226>{online} |"
                                                                       f"<:away:627627415119724554>{idle} |"
                                                                       f"<:dnd:627627404784828416>{dnd} |"
                                                                       f"<:offline:627627415144890389>{offline}\n"
                                                                       f"**Verification level:** {utils.guild_verification_level(guild)}\n"
                                                                       f"**Content filter level:** {utils.guild_content_filter_level(guild)}\n"
                                                                       f"**2FA:** {utils.guild_mfa_level(guild)}\n"
                                                                       f"**Role Count:** {len(guild.roles)}\n", inline=False)
            embed.add_field(name="__**Channels:**__", value=f"**Text channels:** {len(guild.text_channels)}\n"
                                                            f"**Voice channels:** {len(guild.voice_channels)}\n"
                                                            f"**Voice region:** {utils.guild_region(guild)}\n"
                                                            f"**AFK timeout:** {int(guild.afk_timeout / 60)} minutes\n"
                                                            f"**AFK channel:** {guild.afk_channel}\n", inline=False)

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
        title = "Guild id           |Total    |Humans   |Bots     |Percent  |Name\n"

        # Loop through all the guilds the bot can see.
        for guild in sorted(self.bot.guilds, key=key, reverse=True):

            # Count how many members are bot/humans.
            bots = sum(1 for m in guild.members if m.bot)
            humans = sum(1 for m in guild.members if not m.bot)
            total = guild.member_count
            percent = f"{round((bots / total) * 100, 2)}%"

            # Create a message with the current guilds information.
            message = f"{guild.id} |{total}{' ' * int(9 - len(str(total)))}|{humans}{' ' * int(9 - len(str(humans)))}|{bots}{' ' * int(9 - len(str(bots)))}|{percent}{' ' * int(9 - len(str(percent)))}|{guild.name}"

            # Append the message to the list of entries.
            entries.append(message)

        # Paginate the entries.
        return await ctx.paginate_codeblock(entries=entries, entries_per_page=guilds_per_page, title=title)

    @commands.is_owner()
    @commands.command(name="socketstats", aliases=["ss"], hidden=True)
    async def socket_stats(self, ctx):

        # Get the total amount of socket events.
        total = sum(self.bot.socket_stats.values())
        # Get the bots uptime in seconds.
        uptime = round(time.time() - self.bot.start_time)

        # Loop through the socketstats and create a message for it.
        socket_stats = ""
        for event, count in self.bot.socket_stats.items():
            socket_stats += f"{event}:{' ' * int(27 - len(str(event)))}{count}\n"

        # Send a message with the socket stats.
        return await ctx.send(f"```\n"
                              f"{total} socket events observed at a rate of {round(total/(uptime / 60))}/minute\n\n"
                              f"{socket_stats}\n"
                              f"```")

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
