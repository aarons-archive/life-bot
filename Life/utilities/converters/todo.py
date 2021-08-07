from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


class TodoContentConverter(commands.clean_content):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        if not (argument := (await super().convert(ctx=ctx, argument=argument)).strip()):
            raise commands.BadArgument

        if len(argument) > 150:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"Your todo content must be under 150 characters.")

        return argument
