import traceback

import andesite
import discord
from discord.ext import commands

from .utilities import formatting


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        print(f"\n[BOT] Logged in as {self.bot.user} - {self.bot.user.id}\n")

        # Loop through the bots guilds.
        for guild in self.bot.guilds:
            # Check if the guild is in the blacklist.
            if guild.id in self.bot.guild_blacklist:
                # The guild was in the blacklist, so leave it.
                print(f"[BOT] Left blacklisted guild - {guild.id}")
                await guild.leave()
            else:
                # The guild wasn't in the blacklist so skip it.
                continue

    @commands.Cog.listener()
    async def on_resume(self):
        print(f"\n[BOT] Connection resumed.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(f"\n[BOT] Disconnected.")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        # If the edited message is not embedded or pinned, process it, this allows for users to edit commands.
        if not after.embeds and not after.pinned and not before.pinned and not before.embeds:

            # Get the context of the message.
            ctx = await self.bot.get_context(after)

            # If the message was a command.
            if ctx.command:
                # And the author is in the user blacklist, dont process the command.
                if after.author.id in self.bot.user_blacklist:
                    return await after.channel.send(f"Sorry, you are blacklisted.")
                # Otherwise, process the message.
                await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command(self, ctx):

        # If the author is blacklisted, dont let them use this command.
        if ctx.author.id in self.bot.user_blacklist:
            return await ctx.channel.send(f"Sorry, you are blacklisted.")

        # Get the commands full name.
        parent = ctx.command.full_parent_name
        if parent:
            command = f"{parent} {ctx.command.name}"
        else:
            command = f"{ctx.command.name}"

        # If the guild id is not already in the bots usage dict, add it.
        if ctx.guild.id not in self.bot.usage:
            self.bot.usage[ctx.guild.id] = {}
        # If the command is not aleady in the guilds command usage, add it
        if command not in self.bot.usage[ctx.guild.id]:
            self.bot.usage[ctx.guild.id][command] = 1
        # Otherwise increment the command usage by 1.
        else:
            self.bot.usage[ctx.guild.id][command] += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        # If the command has a local error handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # Get the original exception or if nothing is found, keep the original exception.
        error = getattr(error, "original", error)

        # Check for errors.
        message = ""
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"You missed the `{error.param}` parameter. You can use `{ctx.prefix}help {ctx.command}` for more information on what parameters to pass."
        if isinstance(error, commands.TooManyArguments):
            message = f"You passed too many arguments to the command `{ctx.command}`. You can use `{ctx.prefix}help {ctx.command}` for more information on what arguments to pass."
        if isinstance(error, commands.BadArgument):
            message = f"You passed a bad arguement to the command `{ctx.command}`."
        if isinstance(error, commands.PrivateMessageOnly):
            message = f"The command `{ctx.command}` can only be used in DM's."
        if isinstance(error, commands.NoPrivateMessage):
            try:
                message = f"The command `{ctx.command}` can not be used in DM's."
            except discord.Forbidden:
                return
        if isinstance(error, commands.NotOwner):
            message = f"The command `{ctx.command}` is owner only."
        if isinstance(error, commands.MissingPermissions):
            missing_perms = ""
            for perm in error.missing_perms:
                missing_perms += f"\n> {perm}"
            message = f"You don't have the following permissions required to run the command `{ctx.command}`.\n{missing_perms}"
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = ""
            for perm in error.missing_perms:
                missing_perms += f"\n> {perm}"
            message = f"I am missing the following permissions to run the command `{ctx.command}`.\n{missing_perms}"
        if isinstance(error, commands.DisabledCommand):
            message = f"The command `{ctx.command}` is currently disabled."
        if isinstance(error, commands.CommandOnCooldown):
            if error.cooldown.type == commands.BucketType.user:
                message = f"The command `{ctx.command}` is on cooldown for you, retry in `{formatting.get_time_friendly(error.retry_after)}`."
            if error.cooldown.type == commands.BucketType.default:
                message = f"The command `{ctx.command}` is on cooldown for the whole bot, retry in `{formatting.get_time_friendly(error.retry_after)}`."
            if error.cooldown.type == commands.BucketType.guild:
                message = f"The command `{ctx.command}` is on cooldown for this guild, retry in `{formatting.get_time_friendly(error.retry_after)}`."
        if isinstance(error, andesite.NodesUnavailable):
            message = "There are no nodes available."

        # If an error was caught, send it.
        if message:
            return await ctx.send(message)
        # Otherwise, print the original error as a traceback.
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        # Log the guild that was joined.
        print(f"\n[BOT] Joined a guild - {guild.name}")

        # If the guild is the blacklist, leave it.
        if guild.id in self.bot.guild_blacklist:
            print(f"[BOT] Left blacklisted guild - {guild.name}")
            return await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        # Log the guild that was left.
        print(f"\n[BOT] Left a guild - {guild.name}")

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_stats[msg.get('t')] += 1


def setup(bot):
    bot.add_cog(Events(bot))
