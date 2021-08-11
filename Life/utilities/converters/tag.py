from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


class TagNameConverter(commands.clean_content):

    async def convert(self, ctx: context.Context, argument: str) -> str:
        self.escape_markdown = True

        if not (argument := (await super().convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if argument.split(" ")[0] in (names := ctx.bot.get_command("tag").all_commands.keys()):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"Tag names can not start with a tag subcommand name. ({', '.join(f'`{name}`' for name in names)})"
            )
        if len(argument) < 3 or len(argument) > 50:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Tag names must be between 3 and 50 characters long."
            )

        return argument


class TagContentConverter(commands.clean_content):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        if not (argument := (await super().convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if len(argument) > 1500:
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="Tag content can not be more than 1500 characters long."
            )

        return argument
