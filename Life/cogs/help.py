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
        # Get the ctx and owner of bot.
        ctx = self.context
        owner = ctx.bot.get_user(238356301439041536)
        # Define an embed.
        embed = discord.Embed(
            colour=0xFF0000,
            title="__MrBots help page__",
            description=f"Use `{ctx.prefix} help [command]` for more info on a command.\n"
                        f"You can also use `{ctx.prefix} help [category]` for more info on a category.\n"
        )
        # Loop through all the cogs.
        for cog in ctx.bot.cogs.values():
            # If this cogs has no commands or the commands are hidden, goto the next cog.
            if sum(1 for c in cog.get_commands() if not (ctx.author != owner and c.hidden)) == 0:
                continue
            # Add cog name to description.
            embed.description += f"\n__**{cog.qualified_name}:**__\n"
            # Loop through the commands in this cog.
            for command in cog.get_commands():
                # If the author is not the owner.
                if not ctx.author.id == owner.id:
                    # If the command is hidden, skip this command.
                    if command.hidden is True:
                        continue
                    # Add the command to the discription.
                    embed.description += f"{command.name} \u200b "
                # Else, add the command to the discription even if it is hidden.
                else:
                    embed.description += f"{command.name} \u200b "
        # Send the embed.
        return await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        # Get the ctx and owner of bot.
        ctx = self.context
        owner = ctx.bot.get_user(238356301439041536)
        # If this cogs has no commands or the commands are hidden, don"t display the help command.
        if sum(1 for c in cog.get_commands() if not (c.hidden and ctx.author != owner)) == 0:
            return await ctx.send("That extension is hidden/is owner only.")
        # Define an embed.
        embed = discord.Embed(
            colour=0xFF0000,
            title=f"__**{cog.qualified_name} cog help page.**__",
            description=f""
        )
        embed.description += f"Use `{ctx.prefix} help [command]` for more info on a command.\n\n"
        # Loop through all the commands in this cog.
        for command in cog.get_commands():
            # Get the command name along with all its aliases.
            command_name = f"{self.get_full_command(command)}"
            # If the author is not the owner.
            if not ctx.author.id == owner.id:
                # If the command is hidden, skip this command.
                if command.hidden is True:
                    continue
                # If the command has a help string.
                if command.help:
                    # Get the first line of the help string.
                    command_help = f" - " + command.help.strip().split("\n")[0]
                else:
                    # The command did not have a help string.
                    command_help = f" - No help provided for this command."
                # Add command to the embed.
                embed.description += f"**{command_name}**{command_help}\n"
            # Else, add the command to the discription even if it is hidden.
            else:
                # If the command has a help string.
                if command.help:
                    # Get the first line of the help string.
                    command_help = f" - " + command.help.strip().split("\n")[0]
                else:
                    # The command did not have a help string.
                    command_help = f" - No help provided for this command."
                # Add command to the embed.
                embed.description += f"**{command_name}**{command_help}\n"
            # If the command is a group command.
            if isinstance(command, commands.Group):
                # Loop through the command in the group.
                for group_command in command.commands:
                    group_command_name = f"{self.get_full_command(group_command)}"
                    # If the author is not the owner.
                    if not ctx.author.id == owner.id:
                        # If the command is hidden, skip this command.
                        if group_command.hidden is True:
                            continue
                        # If the command has a help string.
                        if group_command.help:
                            # Get the first line of the help string.
                            group_command_help = f" - " + group_command.help.strip().split("\n")[0]
                        else:
                            # The command did not have a help string.
                            group_command_help = f" - No help provided for this command."
                        # Add command to the embed.
                        embed.description += f"**{group_command_name}**{group_command_help}\n"
                    # Else, add the command to the discription even if it is hidden.
                    else:
                        # If the command has a help string.
                        if group_command.help:
                            # Get the first line of the help string.
                            group_command_help = f" - " + group_command.help.strip().split("\n")[0]
                        else:
                            # The command did not have a help string.
                            group_command_help = f" - No help provided for this command."
                        # Add command to the embed.
                        embed.description += f"**{group_command_name}**{group_command_help}\n"
        return await ctx.send(embed=embed)

    async def send_command_help(self, command):
        # Get the ctx.
        ctx = self.context
        # Define an embed.
        embed = discord.Embed(
            colour=0xFF0000,
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
            colour=0xFF0000,
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
    Help with how to understand and use MrBot.
    """

    def __init__(self, bot):
        self.bot = bot
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(Help(bot))
