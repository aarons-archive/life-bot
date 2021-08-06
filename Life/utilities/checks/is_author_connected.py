from typing import Literal

from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


def is_author_connected(same_channel: bool):

    async def predicate(ctx: context.Context) -> Literal[True]:

        author_channel = ctx.author.voice and ctx.author.voice.channel
        voice_client_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if same_channel is True and voice_client_channel is not None and author_channel != voice_client_channel:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"You must be connected to {voice_client_channel.mention} to use this command.")

        if not author_channel:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"You must be connected to a voice channel to use this command.")

        return True

    return commands.check(predicate)
