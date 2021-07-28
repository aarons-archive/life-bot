from typing import Literal

from discord.ext import commands

from core import colours, emojis
from utilities import exceptions, context


def is_voice_client_playing():

    async def predicate(ctx: context.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description='No tracks are currently playing.')

        return True

    return commands.check(predicate)
