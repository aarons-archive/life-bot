from discord.ext import commands
from .utilities import exceptions
from .utilities import formatting
import traceback
import discord


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        print(f"\n[BOT] Logged in as {self.bot.user} - {self.bot.user.id}")

        # Cache the current accounts in the database
        await self.bot.account_manager.cache_all_accounts()

        # Set our user/guild blacklists.
        blacklisted_users = await self.bot.db.fetch("SELECT * FROM user_blacklist")
        blacklisted_guilds = await self.bot.db.fetch("SELECT * FROM guild_blacklist")

        # Append list of blacklisted guilds and users to respecitive lists.
        for user in range(len(blacklisted_users)):
            self.bot.user_blacklist.append(int(blacklisted_users[user]["id"]))
        for user in range(len(blacklisted_guilds)):
            self.bot.guild_blacklist.append(int(blacklisted_guilds[user]["id"]))

        # Leave any guilds that are blacklisted.
        for guild in self.bot.guilds:
            # If the guild is not in the blacklist, skip it.
            if guild.id not in self.bot.guild_blacklist:
                continue
            # The guild was in the blacklist, so leave it.
            print(f"[BOT] Left blacklisted guild - {guild.id}")
            await guild.leave()

    @commands.Cog.listener()
    async def on_resume(self):
        print(f"\n[BOT] Connection resumed.")

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(f"\n[BOT] Disconnected.")

    # noinspection PyUnusedLocal
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # If the edited message is not embedded or pinned, process it, this allows for uses to edit commands.
        if not after.embeds and not after.pinned:

            # Get the context of the message.
            ctx = await self.bot.get_context(after)

            # Handle blacklisted users.
            if ctx.command:
                if after.author.id in self.bot.user_blacklist:
                    return await after.channel.send(f"Sorry, you are blacklisted.")
                await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command(self, ctx):

        # Handle blacklisted users.
        if ctx.author.id in self.bot.user_blacklist:
            return await ctx.channel.send(f"Sorry, you are blacklisted.")

        # Track which commands are used and in which guilds.
        parent = ctx.command.full_parent_name
        if parent:
            command = f"{parent} {ctx.command.name}"
        else:
            command = f"{ctx.command.name}"

        # If the guild id is not already in the stats dict, add it.
        if ctx.guild.id not in self.bot.stats:
            self.bot.stats[ctx.guild.id] = {}
        # If the command is not aleady in the guilds nested dict, add it
        if command not in self.bot.stats[ctx.guild.id]:
            self.bot.stats[ctx.guild.id][command] = 1
        # Else increment the command by 1.
        else:
            self.bot.stats[ctx.guild.id][command] += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # If the command has a local error handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # Get the original exception or if nothing is found keep the exception.
        error = getattr(error, "original", error)

        # Check for errors.
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You missed the `{error.param}` parameter. You can use `{ctx.prefix}help {ctx.command}` for more information on what parameters to pass.")
        if isinstance(error, commands.TooManyArguments):
            await ctx.send(f"You passed too many arguments to the command `{ctx.command}`. You can use `{ctx.prefix}help {ctx.command}` for more information on what arguments to pass.")
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f"You passed a bad arguement to the command `{ctx.command}`.")
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.PrivateMessageOnly):
            return await ctx.send(f"The command `{ctx.command}` can only be used in DM's.")
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f"The command `{ctx.command}` can not be used in DM's.")
            except discord.Forbidden:
                return
        if isinstance(error, commands.NotOwner):
            return await ctx.send(f"The command `{ctx.command}` is owner only.")
        if isinstance(error, commands.MissingPermissions):
            missing_perms = ""
            for perm in error.missing_perms:
                missing_perms += f"\n> {perm}"
            return await ctx.send(f"You don't have the following permissions required to run the command `{ctx.command}`.\n{missing_perms}")
        if isinstance(error, commands.BotMissingPermissions):
            missing_perms = ""
            for perm in error.missing_perms:
                missing_perms += f"\n> {perm}"
            return await ctx.send(f"I am missing the following permissions to run the command `{ctx.command}`.\n{missing_perms}")
        if isinstance(error, commands.DisabledCommand):
            return await ctx.send(f"The command `{ctx.command}` is currently disabled.")
        if isinstance(error, commands.CommandOnCooldown):
            if error.cooldown.type == commands.BucketType.user:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for you, retry in `{formatting.get_time_friendly(error.retry_after)}`.")
            if error.cooldown.type == commands.BucketType.default:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for the whole bot, retry in `{formatting.get_time_friendly(error.retry_after)}`.")
            if error.cooldown.type == commands.BucketType.guild:
                return await ctx.send(f"The command `{ctx.command}` is on cooldown for this guild, retry in `{formatting.get_time_friendly(error.retry_after)}`.")
        if isinstance(error, exceptions.WrongGuild):
            return await ctx.send("This command can't be used in this guild.")

        # Print the error and traceback if it doesnt match any of the above.
        print(f"Ignoring exception in command {ctx.command}:")
        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Log the guild that was joined.
        print(f"\n[BOT] Joined a guild - {guild.name}")

        if guild.id in self.bot.guild_blacklist:
            print(f"[BOT] Left blacklisted guild - {guild.name}")
            return await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # Log the guild that was left.
        print(f"\n[BOT] Left a guild - {guild.name}")


def setup(bot):
    bot.add_cog(Events(bot))
