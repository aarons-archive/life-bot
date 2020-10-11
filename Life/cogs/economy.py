"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import discord
from discord.ext import commands

from bot import Life
from utilities import context


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name='money', aliases=['cash', 'coins'])
    async def money(self, ctx: context.Context, member: discord.Member = None):

        if not member:
            member = ctx.author

        embed = discord.Embed(colour=ctx.user_config.colour)  # dont do this idiot
        embed.description = f'{member.mention} has `£{self.bot.get_user_config(user=member).money}`.'

        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))
