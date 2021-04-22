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
#

import discord
from discord.ext import commands

from bot import Life


class Kross(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.KROSS_GUILD_ID = 491312179476299786
        self.KROSS_LOG_CHANNEL_ID = 736757690239287416

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:

        if member.guild.id != self.KROSS_GUILD_ID:
            return

        channel = self.bot.get_channel(self.KROSS_LOG_CHANNEL_ID)

        if row := await self.bot.db.fetchrow('SELECT * FROM kross_roles WHERE member_id = $1', member.id):

            if not (roles := [member.guild.get_role(role_id) for role_id in row('role_ids') if role_id in list(map(lambda x: x.id, member.guild.roles))]):
                await channel.send(f'{member.mention} just joined. They had roles before they left but none of them are available now.')
                return

            try:
                await member.add_roles(*roles)
                await channel.send(f'{member.mention} just joined and was given `{len(roles)}` role(s) back.')
                await self.bot.db.execute('DELETE FROM kross_roles WHERE member_id = $1', member.id)
            except discord.Forbidden:
                await channel.send(f'{member.mention} just joined. I do not have permission to give them roles or they are above me in the member list.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:

        if member.guild.id != self.KROSS_GUILD_ID:
            return

        channel = self.bot.get_channel(self.KROSS_LOG_CHANNEL_ID)

        if not (role_ids := [role.id for role in member.roles if role.position != 0]):
            await channel.send(f'`{member}` just left. They did not have any roles.')
            return

        await self.bot.db.execute('INSERT INTO kross_roles values ($1, $2)', member.id, role_ids)
        await channel.send(f'`{member}` just left. I have saved their roles.')


def setup(bot: Life) -> None:
    bot.add_cog(Kross(bot=bot))
