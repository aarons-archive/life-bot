"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""
import random

import discord
from discord.ext import commands

from bot import Life
from utilities import context, exceptions, objects


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        ctx = await self.bot.get_context(message)

        if ctx.author.bot:
            return

        if isinstance(ctx.user_config, objects.DefaultUserConfig):
            await self.bot.user_manager.create_user_config(user_id=ctx.author.id)

        await self.bot.user_manager.edit_user_config(user_id=ctx.author.id, attribute='xp', operation='add', value=random.randint(10, 30))

    @commands.command(name='coins', aliases=['money', 'cash'])
    async def coins(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        embed = discord.Embed(colour=ctx.colour, description=f'{member.mention} has `{self.bot.user_manager.get_user_config(user_id=member.id).coins}` coins.')
        await ctx.send(embed=embed)

    @commands.command(name='xp')
    async def xp(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        embed = discord.Embed(colour=ctx.colour, description=f'{member.mention} has `{self.bot.user_manager.get_user_config(user_id=member.id).xp}` xp.')
        await ctx.send(embed=embed)

    @commands.command(name='level')
    async def level(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        embed = discord.Embed(colour=ctx.colour, description=f'{member.mention} is level `{self.bot.user_manager.get_user_config(user_id=member.id).level}`.')
        await ctx.send(embed=embed)

    @commands.command(name='rank')
    async def rank(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        embed = discord.Embed(colour=ctx.colour, description=f'{member.mention} is rank `{self.bot.user_manager.rank(guild_id=ctx.guild.id, user_id=ctx.author.id)}`.')
        await ctx.send(embed=embed)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx: context.Context, leaderboard_type: str = 'xp') -> None:

        if leaderboard_type not in ['level', 'xp', 'coins']:
            raise exceptions.ArgumentError('Leaderboard type must be one of `level`, `xp` or `coins`')

        leaderboard = self.bot.user_manager.leaderboard(guild_id=ctx.guild.id, leaderboard_type=leaderboard_type)
        if not leaderboard:
            raise exceptions.ArgumentError(f'There are no stats for `{leaderboard_type}` in `{ctx.guild}`.')

        entries = []
        for index, (user_id, user_config) in enumerate(leaderboard):

            member = ctx.guild.get_member(user_id)
            entries.append(f'{index + 1:<6} |{getattr(user_config, leaderboard_type):<10} |{str(member)}')

        title = f'Leaderboard for `{leaderboard_type.title()}` in `{ctx.guild}`'
        header = f'Rank   |{leaderboard_type.title():<10} |Name\n'
        await ctx.paginate_embed(entries=entries, per_page=10, header=header, title=title, codeblock=True)


def setup(bot):
    bot.add_cog(Economy(bot))
