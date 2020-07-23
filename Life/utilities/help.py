"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

from typing import Union

import discord
from discord.ext import commands


class HelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__(command_attrs={'help': 'Shows help for the bot, a category or a command.\n\n'
                                                '**<argument>** means the argument is required.\n'
                                                '**[argument]** means the argument is optional.\n'
                                                '**[a|b]** means it can be "A" or "B".\n'
                                                '**[argument...]** means you can have multiple arguments.'
                                        }
                         )

    def get_cog_commands(self, cog: commands.Cog):

        ctx = self.context
        filtered_commands = []

        for command in cog.walk_commands():

            if ctx.author.id in ctx.bot.owner_ids:
                filtered_commands.append(command)  # Show all commands if author is owner.
            elif command.hidden or command.root_parent and command.root_parent.hidden:
                continue  # Skip command if it or its parents are hidden.
            else:
                filtered_commands.append(command)

        return filtered_commands

    def format_commands(self, command_list: list):

        formatted_commands = []

        for command in command_list:

            command_help = command.help.strip().split('\n')[0] if command.help else 'No help provided for this command.'

            space = '\u200b \u200b ' * (len(command.parents) - 1)
            indent = '`╚╡` ' if command.parents else ''
            formatted_commands.append(f'**{space}{indent}{command.name}** - {command_help}')

        return formatted_commands

    async def send_bot_help(self, mapping):

        ctx = self.context
        entries = []

        for cog in sorted(ctx.bot.cogs.values(), key=lambda c: len(list(c.walk_commands())), reverse=True):

            if cog.qualified_name == 'Jishaku':
                continue

            cog_commands = self.get_cog_commands(cog=cog)
            if not cog_commands:
                continue

            cog_help = f'__**{cog.qualified_name}:**__\n'
            cog_help += ''.join([f'`{command.qualified_name}`\u200b ' for command in cog_commands])
            entries.append(cog_help)

        title = f"__{ctx.bot.user.name}'s help page__"
        header = f'Use `{ctx.bot.config.prefix}help [Command/Category]` for help on a command or category.\n'
        await ctx.paginate_embed(title=title, header=header, entries=entries, entries_per_page=5)

    async def send_cog_help(self, cog: commands.Cog):

        ctx = self.context

        cog_commands = self.get_cog_commands(cog=cog)
        if not cog_commands:
            return await ctx.send('That cog has no commands that you are able to see.')

        title = f'__**{cog.qualified_name} help page:**__\n'
        entries = self.format_commands(command_list=cog_commands)
        await ctx.paginate_embed(title=title, entries=entries, entries_per_page=20)

    async def send_group_help(self, group: commands.Group):

        ctx = self.context

        filtered_commands = []

        for command in group.walk_commands():

            if ctx.author.id in ctx.bot.owner_ids:
                filtered_commands.append(command)  # Show all commands if author is owner.
            elif command.hidden or command.root_parent and command.root_parent.hidden:
                continue  # Skip command if it or its parents are hidden.
            else:
                filtered_commands.append(command)

        if not filtered_commands:
            return await ctx.send('That command has no subcommands that you are able to see.')

        command_help = group.help if group.help else 'No help provided for this command.'
        aliases = f'**Aliases:** {"/".join(group.aliases)}\n\n'

        title = f'{group.name} {group.signature if group.signature else ""}'
        header = f'{aliases if group.aliases else ""}{command_help}\n\n__**Subcommands:**__\n'
        entries = self.format_commands(command_list=filtered_commands)

        await ctx.paginate_embed(title=title, header=header, entries=entries, entries_per_page=20)

    async def send_command_help(self, command: commands.Command):

        ctx = self.context

        command_help = command.help if command.help else 'No help provided for this command.'
        aliases = f'**Aliases:** {"/".join(command.aliases)}\n\n'

        title = f'{command.name} {command.signature if command.signature else ""}'
        description = f'{aliases if command.aliases else ""}{command_help}'
        embed = discord.Embed(colour=discord.Colour.gold(), title=title, description=description)

        await ctx.send(embed=embed)

    def command_not_found(self, search: str):
        return f'There are no commands or categories with the name `{search}`. Be sure to capitalize the first ' \
               f'letter if you are looking for the help of a category.'

    def subcommand_not_found(self, command: Union[commands.Command, commands.Group], search: str):

        if isinstance(command, commands.Group):
            return f'The command `{command.qualified_name}` has no sub-commands called `{search}`.'

        return f'The command `{command.qualified_name}` has no sub-commands.'
