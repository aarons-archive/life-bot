"""
Life
Copyright (C) 2020 Axel#3456

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import discord
from discord.ext import commands

from bot import Life


class SystemCollapse(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.guild_id = 350247597862158347

        self.verified_role = discord.Object(768226910903468033)
        self.content_role = discord.Object(768620502297083915)
        self.events_role = discord.Object(768620661563850783)
        self.announcements_role = discord.Object(768620823480893481)

        self.verify_message = discord.Object(768904890042548245)
        self.verify_channel = discord.Object(768233187704176651)

        self.reaction_role_message = discord.Object(768907337888956457)
        self.reaction_role_channel = discord.Object(768619511372841020)

        self.wave_emoji = '\U0001f44b'
        self.bangbang_emoji = '\U0000203c\U0000fe0f'
        self.party_emoji = '\U0001f973'
        self.forward_emoji = '\U000025b6\U0000fe0f'

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:

        if not payload.guild_id == self.guild_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if payload.channel_id == self.verify_channel.id and payload.message_id == self.verify_message.id:

            if payload.emoji.name == self.wave_emoji:
                await member.add_roles(self.verified_role)

        elif payload.channel_id == self.reaction_role_channel.id and payload.message_id == self.reaction_role_message.id:

            if payload.emoji.name == self.party_emoji:
                await member.add_roles(self.events_role)
            elif payload.emoji.name == self.bangbang_emoji:
                await member.add_roles(self.announcements_role)
            elif payload.emoji.name == self.forward_emoji:
                await member.add_roles(self.content_role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:

        if not payload.guild_id == self.guild_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if payload.channel_id == self.verify_channel.id and payload.message_id == self.verify_message.id:

            if payload.emoji.name == self.wave_emoji:
                await member.remove_roles(self.verified_role)

        elif payload.channel_id == self.reaction_role_channel.id and payload.message_id == self.reaction_role_message.id:

            if payload.emoji.name == self.party_emoji:
                await member.remove_roles(self.events_role)
            elif payload.emoji.name == self.bangbang_emoji:
                await member.remove_roles(self.announcements_role)
            elif payload.emoji.name == self.forward_emoji:
                await member.remove_roles(self.content_role)


def setup(bot):
    bot.add_cog(SystemCollapse(bot))
