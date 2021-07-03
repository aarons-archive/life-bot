"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Literal

from discord.ext import commands

from core import colours, emojis
from utilities import context, exceptions


def is_author_connected(same_channel: bool):

    async def predicate(ctx: context.Context) -> Literal[True]:

        author_channel = ctx.author.voice and ctx.author.voice.channel
        voice_client_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if same_channel is True and voice_client_channel is not None:

            if author_channel != voice_client_channel:
                raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"You must be connected to {voice_client_channel.mention} to use this command.")

        if not author_channel:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"You must be connected to a voice channel to use this command.")

        return True

    return commands.check(predicate)
