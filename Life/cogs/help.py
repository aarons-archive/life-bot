from discord.ext import commands
import discord


class HelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__(command_attrs={
            "help": "Shows help about the Bot, an Extension or a Command.\n\n**<arguement>** means the arguement is "
                    "**required.**\n**[arguement]** means the arguement is **optional.**\n**[a|b]** means it can be "
                    "**'A' or 'B'.**\n**[arguement...]** means you can have **multiple arguements.** "
        })

    def get_full_command(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "/".join(command.aliases)
            command_name = f"{command.name}/{aliases}"
            if parent:
                command_name = f"{self.context.prefix}{parent} {command_name}"
            else:
                command_name = f"{self.context.prefix}{command_name}"
        else:
            if parent:
                command_name = f"{self.context.prefix}{parent} {command.name}"
            else:
                command_name = f"{self.context.prefix}{command.name}"
        return command_name

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    async def send_bot_help(self, mapping):

        # Get the current context.
        ctx = self.context

        # Define an embed.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"__{ctx.bot.user.name}'s help page__",
            description=f"Use `{ctx.prefix}help [command/Category]` for more info on a command or category.\n"
        )

        # Loop through all the cogs.
        for cog in ctx.bot.cogs.values():
            # If the author is a bot owner, fetch all commands.
            if ctx.author.id in ctx.bot.owner_ids:
                cog_commands = [command for command in cog.get_commands()]
            # Else, just fetch non hidden commands.
            else:
                cog_commands = [command for command in cog.get_commands() if command.hidden == False]
            # If no commands where found, skip this cog.
            if len(cog_commands) == 0:
                continue
            # Add this cogs name to the embed description.
            embed.description += f"\n__**{cog.qualified_name}:**__\n"
            # Loop through the commands in this cog.
            for command in cog_commands:
                # Add the command to the embeds discription.
                embed.description += f"`{command.name}` \u200b "
        # Send the embed.
        return await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        # Get the current context.
        ctx = self.context

        # Define an embed.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"__{cog.qualified_name} cog help page__",
            description=f"Use `{ctx.prefix}help [command]` for more info on a command.\n\n"
        )

        # If the author is a bot owner, fetch all commands.
        if ctx.author.id in ctx.bot.owner_ids:
            cog_commands = [command for command in cog.get_commands()]
        # Else, just fetch non hidden commands.
        else:
            cog_commands = [command for command in cog.get_commands() if command.hidden == False]

        # If no commands where found, return an error.
        if len(cog_commands) == 0:
            return await ctx.send("This cog has no commands. This could be because they are hidden, or there are just no commands.")

        for command in cog_commands:
            command_name = self.get_full_command(command)
            if command.help:
                command_help = command.help.strip().split("\n")[0]
            else:
                command_help = "No help provided for this command."
            embed.description += f"**{command_name}** - {command_help}\n"
            if isinstance(command, commands.Group):
                for group_command in command.commands:
                    group_command_name = self.get_full_command(group_command)
                    if group_command.help:
                        group_command_help = group_command.help.strip().split("\n")[0]
                    else:
                        group_command_help = "No help provided for this command."
                    embed.description += f"`⮡\u200b` **{group_command_name}** - {group_command_help}\n"
        return await ctx.send(embed=embed)

    async def send_command_help(self, command):
        # Get the ctx.
        ctx = self.context
        # Define an embed.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"",
            description=""
        )
        # Get the commands aliases.
        command_name = f"{self.get_full_command(command)}"
        # If the command has a help string.
        if command.help:
            # Get the first line of the help string.
            command_help = f"{command.help}"
        # The command did not have a help string.
        else:
            command_help = f"No help provided for this command."
        # If the command has any parameters.
        if command.signature:
            # Add the command with params + help to the embed
            embed.title += f"{command_name} {command.signature}:"
            embed.description += f"{command_help}\n"
        # The command didnt have any parameters.
        else:
            # Add the command with the help to the embed
            embed.title += f"{command_name}:"
            embed.description += f"{command_help}\n"
        return await ctx.send(embed=embed)

    async def send_group_help(self, group):
        # Get the ctx.
        ctx = self.context
        # Define an embed.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"",
            description=""
        )
        # Get the commands aliases.
        group_name = f"{self.get_full_command(group)}"
        # If the command has a help string.
        if group.help:
            # Get the first line of the help string.
            group_help = group.help.strip().split("\n")[0]
        # The command did not have a help string.
        else:
            group_help = f"No help provided for this command."
        # If the command has any parameters.
        if group.signature:
            # Add the command with params + help to the embed
            embed.title += f"{group_name} {group.signature}:"
            embed.description += f"{group_help}\n\n"
        # The command didnt have any parameters.
        else:
            # Add the command with the help to the embed
            embed.title += f"{group_name}:"
            embed.description += f"{group_help}\n\n"
        # Loop through the commands in the group.
        for command in group.commands:
            group_command_name = f"**{self.get_full_command(command)}**"
            # If the command has a help string.
            if command.help:
                # Get the first line of the help string.
                group_command_help = f" - " + command.help.strip().split("\n")[0]
            else:
                # The command did not have a help string.
                group_command_help = f" - No help provided for this command."
            # Add command to the embed.
            embed.description += f"**{group_command_name}**{group_command_help}\n"

        return await ctx.send(embed=embed)


class Help(commands.Cog):
    """
    Help with how to understand and use Life.
    """

    def __init__(self, bot):
        self.bot = bot
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(Help(bot))
