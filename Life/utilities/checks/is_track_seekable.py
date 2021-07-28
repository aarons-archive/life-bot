from typing import Literal

from discord.ext import commands

from core import colours, emojis
from utilities import exceptions, context


def is_track_seekable():

    async def predicate(ctx: context.Context) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.current or not ctx.voice_client.current.is_seekable():
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="The current track is not seekable.")

        return True

    return commands.check(predicate)
