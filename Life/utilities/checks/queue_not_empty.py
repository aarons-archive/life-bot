from typing import Literal

from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


def queue_not_empty():

    async def predicate(ctx: context.Context) -> Literal[True]:

        if not ctx.voice_client or ctx.voice_client.queue.is_empty():
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="The queue is empty.")

        return True

    return commands.check(predicate)
