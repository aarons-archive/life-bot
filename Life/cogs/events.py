import traceback

import discord
import granitepy
from discord.ext import commands

from utilities import utils


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        print(f"\n[BOT] Logged in as {self.bot.user} - {self.bot.user.id}")

        for guild in self.bot.guilds:

            if guild.id in self.bot.guild_blacklist:
                print(f"[BOT] Left blacklisted guild - {guild.id}")
                await guild.leave()
            else:
                continue

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(f"[BOT] Disconnected from discord")

    @commands.Cog.listener()
    async def on_connect(self):
        print(f"[BOT] Connected to discord.")

    @commands.Cog.listener()
    async def on_resume(self):
        print(f"[BOT] Resumed a session.")

    @commands.Cog.listener()
    async def on_command(self, ctx):

        parent = ctx.command.full_parent_name
        if parent:
            command = f"{parent} {ctx.command.name}"
        else:
            command = f"{ctx.command.name}"

        if ctx.guild.id not in self.bot.usage:
            self.bot.usage[ctx.guild.id] = {}
        if command not in self.bot.usage[ctx.guild.id]:
            self.bot.usage[ctx.guild.id][command] = 1
        else:
            self.bot.usage[ctx.guild.id][command] += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # Get the original exception or if nothing is found, keep the original exception.
        error = getattr(error, "original", error)

        # Check for errors.
        message = ""
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CheckFailure):
            message = f"{error}"
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"You missed the `{error.param}` parameter. You can use `{ctx.prefix}help {ctx.command}` for more information on what parameters to pass."
        if isinstance(error, commands.TooManyArguments):
            message = f"You passed too many arguments to the command `{ctx.command}`. You can use `{ctx.prefix}help {ctx.command}` for more information on what arguments to pass."
        if isinstance(error, commands.BadArgument):
            message = f"You passed a bad arguement to the command `{ctx.command}`."
        if isinstance(error, commands.PrivateMessageOnly):
            message = f"The command `{ctx.command}` can only be used in DM's."
        if isinstance(error, commands.NotOwner):
            message = f"The command `{ctx.command}` is owner only."
        if isinstance(error, commands.DisabledCommand):
            message = f"The command `{ctx.command}` is currently disabled."
        if isinstance(error, granitepy.NoNodesAvailable):
            message = "There are no nodes available."

        if isinstance(error, commands.NoPrivateMessage):
            try:
                message = f"The command `{ctx.command}` can not be used in DM's."
            except discord.Forbidden:
                return
        if isinstance(error, commands.MissingPermissions):
            missing_perms = ">>> \n"
            for perm in error.missing_perms:
                missing_perms += f"{perm}\n"
            message = f"You don't have the following permissions required to run the command `{ctx.command}`.\n{missing_perms}"
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = ">>> \n"
            for perm in error.missing_perms:
                missing_perms += f"{perm}\n"
            message = f"I am missing the following permissions to run the command `{ctx.command}`.\n{missing_perms}"
        if isinstance(error, commands.CommandOnCooldown):
            if error.cooldown.type == commands.BucketType.user:
                message = f"The command `{ctx.command}` is on cooldown for you, retry in `{utils.format_time(error.retry_after)}`."
            if error.cooldown.type == commands.BucketType.default:
                message = f"The command `{ctx.command}` is on cooldown for the whole bot, retry in `{utils.format_time(error.retry_after)}`."
            if error.cooldown.type == commands.BucketType.guild:
                message = f"The command `{ctx.command}` is on cooldown for this guild, retry in `{utils.format_time(error.retry_after)}`."

        # If an error was found, send it.
        if message:
            return await ctx.send(message)

        # Otherwise, print the original error as a traceback.
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        if guild.id in self.bot.guild_blacklist:
            print(f"[BOT] Left blacklisted guild - {guild.name}")
            return await guild.leave()

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_stats[msg.get('t')] += 1


def setup(bot):
    bot.add_cog(Events(bot))
