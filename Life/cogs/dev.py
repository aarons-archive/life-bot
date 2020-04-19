import collections
import sys

import asyncpg
import discord
import humanize
import pkg_resources
import psutil
import setproctitle
from discord.ext import commands


class Dev(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        setproctitle.setproctitle("LifeBot")

    async def cog_check(self, ctx):
        if ctx.author.id in self.bot.owner_ids:
            return True
        return False

    @commands.group(name="dev", hidden=True, invoke_without_command=True)
    async def dev(self, ctx):
        """
        Base command for Life developer commands.
        """

        embed = discord.Embed(title=f"{self.bot.user.name} bot information page.", colour=0xF5F5F5)

        embed.description = f"I am running on the python version **{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}** " \
                            f"on the OS **{sys.platform}** using the discord.py version **{pkg_resources.get_distribution('discord.py').version}**. " \
                            f"The process is running as **{setproctitle.getproctitle()}** on PID **{self.bot.process.pid}** and is " \
                            f"using **{self.bot.process.num_threads()}** threads.\n\n"

        summary = f"**{len(self.bot.guilds)}** guilds and **{len(self.bot.users)}** users."
        if isinstance(self.bot, commands.AutoShardedBot):
            embed.description += f"The bot is automatically sharded with **{self.bot.shard_count}** shard(s) and can see {summary}\n\n"
        else:
            embed.description += f"The bot is not sharded and can see {summary}\n\n"

        with self.bot.process.oneshot():

            memory_usage = self.bot.process.memory_full_info()
            cpu_usage = self.bot.process.cpu_percent(interval=None)

            embed.description += f"The process is using " \
                                 f"**{humanize.naturalsize(memory_usage.rss)}** of physical memory, " \
                                 f"**{humanize.naturalsize(memory_usage.vms)}** of virtual memory and " \
                                 f"**{humanize.naturalsize(memory_usage.uss)}** of memory that is unique " \
                                 f"to the process. It is also using **{cpu_usage}%** of CPU across " \
                                 f"**{psutil.cpu_count(logical=False)}** cores."

        return await ctx.send(embed=embed)

    @dev.command(name="guilds", hidden=True)
    async def dev_guilds(self, ctx, guilds_per_page: int = 20):
        """
        Display a list of guilds with the percentage of bots to normal accounts in them.

        `guilds_per_page`: The amount of guilds to show per page.
        """

        def key(guild_check):
            guild_bots = sum(1 for m in guild_check.members if m.bot)
            guild_members = len(guild_check.members)
            return round((guild_bots / guild_members) * 100, 2)

        entries = []

        for guild in sorted(self.bot.guilds, key=key, reverse=True):

            total = len(guild.members)
            bots = sum(1 for m in guild.members if m.bot)
            humans = sum(1 for m in guild.members if not m.bot)
            bot_percent = f"{round((bots / total) * 100, 2)}%"

            entries.append(f"{guild.id} |{total:<9}|{humans:<9}|{bots:<9}|{bot_percent:9}|{guild.name}")

        header = "Guild id           |Total    |Humans   |Bots     |Percent  |Name\n"
        return await ctx.paginate_codeblock(entries=entries, entries_per_page=guilds_per_page, header=header)

    @dev.command(name="socketstats", aliases=["ss"], hidden=True)
    async def dev_socket_stats(self, ctx):
        """
        Display a list of events and how many times they have been received since startup.
        """

        embed = discord.Embed(title=f"{self.bot.user.name} bot socket-stats.", colour=0xF5F5F5)

        socket_stats = collections.OrderedDict(sorted(self.bot.socket_stats.items(), key=lambda kv: kv[1], reverse=True))

        embed.description = f"```py\n{sum(socket_stats.values())} socket events observed at a rate of {round(sum(socket_stats.values()) / self.bot.uptime)} per second.\n\n"
        for event, count in socket_stats.items():
            embed.description += f"{event:28} | {count}\n"
        embed.description += "```"

        return await ctx.send(embed=embed)

    @dev.group(name="blacklist", aliases=["bl"], hidden=True, invoke_without_command=True)
    async def dev_blacklist(self, ctx):
        """
        Base command for blacklisting.
        """

        return await ctx.send(f"Please choose a valid subcommand. Use `{self.bot.config.PREFIX}help dev blacklist` for more information.")

    @dev_blacklist.command(name="reload", hidden=True)
    async def dev_blacklist_reload(self, ctx):
        """
        Reload the bot's blacklist.
        """

        blacklisted_users = await self.bot.db.fetch("SELECT * FROM blacklist WHERE type = $1", "user")
        for user in blacklisted_users:
            self.bot.user_blacklist[user["id"]] = user["reason"]
        print(f"\n[BLACKLIST] Reloaded user blacklist. [{len(blacklisted_users)} users]")

        blacklisted_guilds = await self.bot.db.fetch("SELECT * FROM blacklist WHERE type = $1", "guild")
        for guild in blacklisted_guilds:
            self.bot.guild_blacklist[guild["id"]] = guild["reason"]
        print(f"[BLACKLIST] Reloaded guild blacklist. [{len(blacklisted_guilds)} guilds]\n")

        return await ctx.send("Reloaded the blacklists.")

    @dev_blacklist.group(name="user", hidden=True, invoke_without_command=True)
    async def dev_blacklist_user(self, ctx):
        """
        Display a list of all blacklisted users.
        """

        blacklisted = []

        blacklist = await self.bot.db.fetch("SELECT * FROM blacklist WHERE type = $1", "user")

        if not blacklist:
            return await ctx.send("No blacklisted users.")

        for entry in blacklist:
            user = self.bot.get_user(entry["id"])
            if not user:
                blacklisted.append(f"User not found - {entry['id']} - Reason: {entry['reason']}")
            else:
                blacklisted.append(f"{user.name} - {user.id} - Reason: {entry['reason']}")

        return await ctx.paginate_codeblock(entries=blacklisted, entries_per_page=10, title=f"Showing {len(blacklisted)} blacklisted users.\n\n")

    @dev_blacklist_user.command(name="add", hidden=True)
    async def dev_blacklist_user_add(self, ctx, user: int = None, *, reason: str = None):
        """
        Add a user to the blacklist.

        `user`: The users id.
        `reason`: Why the user is blacklisted.
        """

        if not reason:
            reason = "No reason"

        if len(reason) > 512:
            return await ctx.caution("The reason can't be more than 512 characters.")

        if not user:
            return await ctx.send("You must specify a user's id.")

        try:
            user = await self.bot.fetch_user(user)
            self.bot.user_blacklist[user.id] = reason
            await self.bot.db.execute("INSERT INTO blacklist (id, type, reason) VALUES ($1, $2, $3)", user.id, "user", reason)
            return await ctx.send(f"User: `{user.name} - {user.id}` has been blacklisted with reason `{reason}`")

        except asyncpg.UniqueViolationError:
            return await ctx.send("That user is already blacklisted.")

    @dev_blacklist_user.command(name="remove", hidden=True)
    async def dev_blacklist_user_remove(self, ctx, user: int = None):
        """
        Remove a user from the blacklist.

        `user`: The users id.
        """

        if not user:
            return await ctx.send("You must specify a user's id.")

        try:
            user = await self.bot.fetch_user(user)
            del self.bot.user_blacklist[user.id]
            await self.bot.db.execute("DELETE FROM blacklist WHERE id = $1", user.id)
            return await ctx.send(f"User: `{user.name} - {user.id}` has been un-blacklisted.")
        except ValueError:
            return await ctx.send(f"User: `{user.name} - {user.id}` is not blacklisted.")

    @dev_blacklist.group(name="guild", hidden=True, invoke_without_command=True)
    async def dev_blacklist_guild(self, ctx):
        """
        Display a list of all blacklisted guilds.
        """

        blacklisted = []

        blacklist = await self.bot.db.fetch("SELECT * FROM blacklist WHERE type = $1", "guild")

        if not blacklist:
            return await ctx.send("No blacklisted guilds.")

        for entry in blacklist:
            guild = self.bot.get_guild(entry["id"])
            if not guild:
                blacklisted.append(f"Guild not found - {entry['id']} - Reason: {entry['reason']}")
            else:
                blacklisted.append(f"{guild.name} - {guild.id} - Reason: {entry['reason']}")

        return await ctx.paginate_codeblock(entries=blacklisted, entries_per_page=10, title=f"Showing {len(blacklisted)} blacklisted guilds.\n\n")

    @dev_blacklist_guild.command(name="add", hidden=True)
    async def dev_blacklist_guild_add(self, ctx, guild: int = None, *, reason: str = None):
        """
        Add a guild to the blacklist.

        `user`: The guilds id.
        `reason`: Why the guild is blacklisted.
        """

        if not reason:
            reason = "No reason"

        if len(reason) > 512:
            return await ctx.caution("The reason can't be more than 512 characters.")

        if not guild:
            return await ctx.send("You must specify a guild's id.")

        try:

            self.bot.user_blacklist[guild] = reason
            await self.bot.db.execute("INSERT INTO blacklist (id, type, reason) VALUES ($1, $2, $3)", guild, "guild", reason)

            try:
                guild = await self.bot.fetch_guild(guild)
                await guild.leave()
            except discord.Forbidden:
                pass

            return await ctx.send(f"Guild: `{guild}` has been blacklisted with reason `{reason}`")

        except asyncpg.UniqueViolationError:
            return await ctx.send("That guild is already blacklisted.")

    @dev_blacklist_guild.command(name="remove", hidden=True)
    async def dev_blacklist_guild_remove(self, ctx, guild: int = None):
        """
        Remove a guild from the blacklist.

        `user`: The guilds id.
        """

        if not guild:
            return await ctx.send("You must specify a guild's id.")

        try:
            del self.bot.user_blacklist[guild]
            await self.bot.db.execute("DELETE FROM blacklist WHERE id = $1", guild)
            return await ctx.send(f"Guild: `{guild}` has been un-blacklisted.")
        except ValueError:
            return await ctx.send(f"Guild: `{guild}` is not blacklisted.")


def setup(bot):
    bot.add_cog(Dev(bot))
