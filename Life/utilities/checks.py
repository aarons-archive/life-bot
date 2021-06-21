#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.

from __future__ import annotations

from typing import Literal

from discord.ext import commands

from utilities import exceptions


def is_connected(same_channel: bool = False):

    async def predicate(ctx) -> Literal[True]:

        if not (channel := getattr(ctx.author.voice, 'channel', None)):

            message = 'You must be connected to a voice channel to use this command.'
            if same_channel and getattr(channel, 'id', None) != getattr(getattr(ctx.voice_client, 'channel', None), 'id', None):
                message = 'You must be connected to the same voice channel as me to use this command.'
            raise exceptions.VoiceError(message)

        return True

    return commands.check(predicate)


def has_voice_client(try_join: bool = False):

    async def predicate(ctx) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_connected:

            if try_join:
                await ctx.invoke(ctx.bot.get_command('join'))
            else:
                raise exceptions.VoiceError('I am not connected to any voice channels.')

        return True

    return commands.check(predicate)


def is_voice_client_playing():

    async def predicate(ctx) -> Literal[True]:

        if not ctx.voice_client or not ctx.voice_client.is_playing:
            raise exceptions.VoiceError('No tracks are currently playing.')

        return True

    return commands.check(predicate)


def is_track_requester():

    async def predicate(ctx) -> bool:

        return getattr(getattr(getattr(ctx.voice_client, 'current', None), 'requester', None), 'id', None) == ctx.author.id

    return commands.check(predicate)


def is_guild_owner():

    def predicate(ctx) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)


def has_any_permissions(**permissions):
    return commands.check_any(*(commands.has_permissions(**{permission: value}) for permission, value in permissions.items()))
