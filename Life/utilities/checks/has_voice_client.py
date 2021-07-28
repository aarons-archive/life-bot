from typing import Literal

from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions

from utilities.checks.is_author_connected import is_author_connected


def has_voice_client(try_join: bool):

    async def predicate(ctx: context.Context) -> Literal[True]:

        if not ctx.voice_client or ctx.voice_client.is_connected() is False:

            if try_join:
                await is_author_connected(same_channel=False).predicate(ctx)
                await ctx.invoke(ctx.bot.get_command('join'))
            else:
                raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description='I am not connected to any voice channels.')

        return True

    return commands.check(predicate)
