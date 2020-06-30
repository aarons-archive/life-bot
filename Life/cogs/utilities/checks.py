"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

from discord.ext import commands


def is_player_playing():
    async def predicate(ctx):
        if not ctx.player.is_playing:
            raise commands.CheckFailure(f'I am not currently playing anything.')
        return True
    return commands.check(predicate)


def is_player_connected():
    async def predicate(ctx):
        if not ctx.player.is_connected:
            raise commands.CheckFailure(f'I am not connected to any voice channels.')
        return True
    return commands.check(predicate)


def is_member_in_channel():
    async def predicate(ctx):
        if not ctx.player.voice_channel == ctx.author.voice.channel:
            raise commands.CheckFailure(f'You are not connected to the same voice channel as me.')
        return True
    return commands.check(predicate)


def is_member_connected():
    async def predicate(ctx):
        if not ctx.author.voice:
            raise commands.CheckFailure(f'You are not connected to any voice channels.')
        return True
    return commands.check(predicate)

