from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


class PrefixConverter(commands.clean_content):

    async def convert(self, ctx: context.Context, argument: str) -> str:
        self.escape_markdown = True

        if not (argument := (await super().convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if "`" in argument:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Your prefix can not contain backtick characters.")
        if len(argument) > 15:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Your prefix can not be more than 15 characters.")

        return argument
