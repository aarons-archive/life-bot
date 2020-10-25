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
import typing
from discord.ext import commands

from bot import Life
from utilities import context, exceptions, objects


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        await self.bot.user_manager.add_xp(user_id=message.author.id)

    @commands.Cog.listener()
    async def on_xp_level_up(self, user_id: int, user_config: objects.UserConfig) -> None:

        if user_config.level_up_notifications is False:
            return

        user = self.bot.get_user(id=user_id)
        try:
            await user.send(f'Congrats, you are now level `{user_config.level}`!')
        except discord.Forbidden:
            return

    #

    @commands.command(name='profile')
    async def profile(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        user_config = self.bot.user_manager.get_user_config(user_id=member.id)

        embed = discord.Embed(colour=user_config.colour,
                              title=f'{member}\'s profile',
                              description=f'`Total xp:` {user_config.xp}\n'
                                          f'`Next level xp:` {user_config.next_level_xp}'
                                          f'`Level:` {user_config.level}\n'
                                          f'`Coins:` {user_config.coins}\n'
                                          f'`Rank (server):` {self.bot.user_manager.rank(user_id=member.id, guild_id=ctx.guild.id)}\n'
                                          f'`Rank (global):` {self.bot.user_manager.rank(user_id=member.id)}')

        await ctx.send(embed=embed)

    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx: context.Context, leaderboard_type: typing.Literal['xp', 'level', 'coins'] = 'xp', global_leaderboard: bool = False) -> None:

        if global_leaderboard is True:
            leaderboard = self.bot.user_manager.leaderboard(leaderboard_type=leaderboard_type)
            title = f'`{leaderboard_type.title()}` leaderboard across the whole bot.'
        else:
            leaderboard = self.bot.user_manager.leaderboard(leaderboard_type=leaderboard_type, guild_id=ctx.guild.id)
            title = f'`{leaderboard_type.title()}` leaderboard in `{ctx.guild}`'

        if not leaderboard:
            raise exceptions.ArgumentError(f'There are no leaderboard stats.')

        entries = []
        for index, (user_id, user_config) in enumerate(leaderboard):
            entries.append(f'{index + 1:<6} |{getattr(user_config, leaderboard_type):<10} |{ctx.bot.get_user(user_id)}')

        header = f'Rank   |{leaderboard_type.title():<10} |Name\n'
        await ctx.paginate_embed(entries=entries, per_page=10, header=header, title=title, codeblock=True)

    @commands.command(name='rank')
    async def rank(self, ctx: context.Context, member: typing.Optional[discord.Member], global_rank: bool = False) -> None:

        if not member:
            member = ctx.author

        if global_rank is True:
            rank = self.bot.user_manager.rank(user_id=member.id)
            message = f'{member} is rank `{rank}` across the whole bot.'
        else:
            rank = self.bot.user_manager.rank(user_id=member.id, guild_id=ctx.guild.id)
            message = f'{member} is rank `{rank}` in this server.'

        await ctx.send(message)

    #

    @commands.command(name='coins', aliases=['money', 'cash'])
    async def coins(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        await ctx.send(f'{member} has `{self.bot.user_manager.get_user_config(user_id=member.id).coins}` coins.')

    @commands.command(name='xp')
    async def xp(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        await ctx.send(f'{member} has `{self.bot.user_manager.get_user_config(user_id=member.id).xp}` xp.')

    @commands.command(name='level')
    async def level(self, ctx: context.Context, member: discord.Member = None) -> None:

        if not member:
            member = ctx.author

        await ctx.send(f'{member} is level `{self.bot.user_manager.get_user_config(user_id=member.id).level}`.')


def setup(bot):
    bot.add_cog(Economy(bot))
