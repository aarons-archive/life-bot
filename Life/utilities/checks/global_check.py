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

from core import colours, emojis, values
from utilities import context, exceptions


async def global_check(ctx: context.Context) -> Literal[True]:

    if ctx.user_config.blacklisted is True or ctx.guild_config.blacklisted is True:
        raise exceptions.EmbedError(
                colour=colours.RED,
                description=f'{emojis.CROSS} {values.ZWSP} You are blacklisted from using this bot.\n\n'
                            f'*If you would like to appeal this please join my [support server]({values.SUPPORT_LINK}).*'

        )

    current = dict(ctx.channel.permissions_for(ctx.me))
    if not ctx.guild:
        current['read_messages'] = True

    needed = {permission: value for permission, value in values.PERMISSIONS if value is True}

    if missing := [permission for permission, value in needed.items() if current[permission] != value]:
        raise commands.BotMissingPermissions(missing)

    return True
