import discord
from discord.ext import commands


class HelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__(command_attrs={
            'help': 'Shows help about the Bot, an Extension or a Command.\n\n'
                    '**<argument>** means the argument is **required**.\n'
                    '**[argument]** means the argument is **optional**.\n'
                    '**[a|b]** means it can be **"A" or "B"**.\n'
                    '**[argument...]** means you can have **multiple arguments**.'
        })

    def formatter(self, command_list, aliases=True, short_name=False, level=0):

        for command in command_list:

            command_name = self.get_command(command, aliases, short_name)

            if command.help:
                command_help = command.help.strip().split('\n')[0]
            else:
                command_help = 'No help provided for this command.'

            indent = ''
            arrow = ''
            if level > 1:
                indent = '\u200b ' * level * 1
            if level > 0:
                arrow = '`╚╡`'

            yield f'{indent}{arrow}**{command_name}** - {command_help}'

            if isinstance(command, commands.Group):
                yield from self.formatter(command.commands, aliases=False, short_name=True, level=level + 1)

    def get_command(self, command, aliases, short_name):

        command_name = f'{self.context.bot.config.PREFIX}'

        command_parents = command.parents
        for command_parent in command_parents[::-1]:
            if short_name is True:
                command_names = command_parent.aliases + [command_parent.name]
                command_name += f'{min(command_names)} '
            elif aliases is True:
                command_aliases = '/'.join([command_parent.name] + command_parent.aliases)
                command_name += f'{command_aliases} '
        if short_name is True:
            command_names = command.aliases + [command.name]
            command_name += f'{min(command_names, key=len)} '
        elif aliases is True:
            command_aliases = '/'.join([command.name] + command.aliases)
            command_name += f'{command_aliases} '

        return command_name

    async def send_bot_help(self, mapping):

        ctx = self.context

        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f"__{ctx.bot.user.name}'s help page__",
            description=f'Use `{ctx.bot.config.PREFIX}help [Command/Category]` for more info on a command/category.\n'
        )

        def key(e):
            return len(e.get_commands())

        for cog in sorted(ctx.bot.cogs.values(), key=key, reverse=True):

            if ctx.author.id in ctx.bot.owner_ids:
                cog_commands = [command for command in cog.get_commands()]
            else:
                cog_commands = [command for command in cog.get_commands() if command.hidden is False]

            if len(cog_commands) == 0:
                continue
            embed.description += f'\n__**{cog.qualified_name}:**__\n'

            for command in cog_commands:
                embed.description += f'`{command.name}` \u200b '

        return await ctx.send(embed=embed)

    async def send_cog_help(self, cog):

        ctx = self.context

        if ctx.author.id in ctx.bot.owner_ids:
            cog_commands = [command for command in cog.get_commands()]
        else:
            cog_commands = [command for command in cog.get_commands() if command.hidden is False]

        if len(cog_commands) == 0:
            message = 'This cog has no commands. This could be because they are hidden, or there are just no commands.'
            return await ctx.send(message)

        return await ctx.paginate_embed(title=f'__**{cog.qualified_name} cog help page:**__\n\n',
                                        entries=list(self.formatter(cog_commands)), entries_per_page=15)

    async def send_command_help(self, command):

        ctx = self.context

        embed = discord.Embed(
            colour=discord.Color.gold(),
            title=f'',
            description=f''
        )

        command_name = self.get_command(command, aliases=True, short_name=False)

        if command.signature:
            embed.title += f'{command_name}{command.signature}'
        else:
            embed.title += f'{command_name}'

        if command.help:
            embed.description += f'{command.help}\n'
        else:
            embed.description += f'No help provided for this command.\n'

        return await ctx.send(embed=embed)

    async def send_group_help(self, group):

        ctx = self.context

        group_name = self.get_command(group, aliases=True, short_name=False)

        if group.signature:
            embed_title = f'{group_name}{group.signature}'
        else:
            embed_title = f'{group_name}'

        if group.help:
            embed_description = f'{group.help}'
        else:
            embed_description = f'No help provided for this command.'

        return await ctx.paginate_embed(title=f'**{embed_title}**', header=f'{embed_description}\n\n',
                                        entries=list(self.formatter(group.commands)), entries_per_page=15)


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.help_command = HelpCommand()
        bot.help_command.cog = self


def setup(bot):
    bot.add_cog(Help(bot))
