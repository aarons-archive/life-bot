# Future
from __future__ import annotations

# Packages
from discord.ext import commands

# My stuff
from core import colours, config
from utilities import custom, exceptions, utils


class HelpCommand(commands.HelpCommand):

    def __init__(self) -> None:

        self.context: custom.Context = utils.MISSING

        super().__init__(
            command_attrs={
                "help": "Shows help for the bot, a category, or a command."
            },
        )

    #

    def filter_command_list(
        self,
        command_list: list[commands.Command, commands.Group],
        /,
    ) -> list[commands.Command | commands.Group]:

        return [
            command for command in command_list
            if not command.hidden
            and not (command.root_parent and command.root_parent.hidden)
            or (self.context.author.id in config.OWNER_IDS)
        ]

    #

    async def send_bot_help(self, mapping: dict[commands.Cog | None, commands.Command]) -> None:

        if not self.context.bot.cogs:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="There are no loaded categories."
            )

        entries = []

        for cog in sorted(self.context.bot.cogs.values(), key=lambda c: len(self.filter_command_list(list(c.walk_commands()))), reverse=True):

            if cog.qualified_name == "Jishaku":
                continue

            if not (cog_commands := self.filter_command_list(list(cog.walk_commands()))):
                continue

            entries.append(
                (
                    f"● **{cog.qualified_name}**",
                    f"{', '.join(f'`{command.qualified_name}`' for command in cog_commands)}"
                )
            )

        await self.context.paginate_fields(
            entries=entries,
            per_page=3,
            title=f"{self.context.bot.user.name} - Commands",
            embed_footer=f"Total commands: {len(self.filter_command_list(list(self.context.bot.walk_commands())))}",
            thumbnail=utils.avatar(self.context.bot.user) if self.context.bot.user else None,
        )

    async def send_cog_help(self, cog: commands.Cog) -> None:

        if not (cog_commands := self.filter_command_list(list(cog.walk_commands()))):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"**{cog.qualified_name}** has no available commands.",
            )

        await self.context.paginate_fields(
            entries=[
                (
                    f"● {command.qualified_name} {' '.join([f'[{name}]' for name in command.clean_params.keys()])}",
                    f"{command.short_doc or 'No help provided for this command.'}"
                ) for command in cog_commands
            ],
            per_page=7,
            title=f"{cog.qualified_name} - Commands",
            header=f"{cog.description or 'No description provided for this category.'}\n",
            embed_footer=f"Total commands: {len(cog_commands)}"
        )

    async def send_group_help(self, group: commands.Group) -> None:

        if not (group_commands := self.filter_command_list(list(group.walk_commands()))):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"**{group.qualified_name}** has no available subcommands.",
            )

        aliases = f"**Aliases:** {'/'.join(group.aliases)}\n\n" if group.aliases else ""

        await self.context.paginate_fields(
            entries=[
                (
                    f"● {command.qualified_name} {' '.join([f'[{name}]' for name in command.clean_params.keys()])}",
                    f"{command.short_doc or 'No help provided for this subcommand.'}"
                ) for command in group_commands
            ],
            per_page=5,
            title=f"{group.qualified_name} {' '.join([f'[{name}]' for name in group.clean_params.keys()])}",
            header=f"{aliases}{group.help or 'No help provided for this group command.'}\n\n**Subcommands:**\n",
            embed_footer=f"Total subcommands: {len(group_commands)}"
        )

    async def send_command_help(self, command: commands.Command) -> None:

        aliases = f"**Aliases:** {'/'.join(command.aliases)}\n\n" if command.aliases else ""

        embed = utils.embed(
            title=f"{command.qualified_name} {' '.join([f'[{name}]' for name in command.clean_params.keys()])}",
            description=f"{aliases}{command.help or 'No help provided for this command.'}"
        )

        await self.context.send(embed=embed)

    #

    def command_not_found(self, string: str) -> str:
        return f"There are no commands or categories with the name **{string}**."

    def subcommand_not_found(self, command: commands.Command | commands.Group, string: str) -> str:

        if isinstance(command, commands.Group):
            return f"The command **{command.qualified_name}** has no sub-commands called **{string}**."

        return f"The command **{command.qualified_name}** has no sub-commands."
