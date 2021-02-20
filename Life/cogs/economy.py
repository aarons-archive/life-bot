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
import random
from typing import Literal, Optional

import discord
import pendulum
from discord.ext import commands

from bot import Life
from utilities import context, enums, exceptions, objects, utils


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.claims = {
            'daily': {
                'collected': enums.Updateable.DAILY_COLLECTED,
                'streak': enums.Updateable.DAILY_STREAK,
                'days_before_claimable': 1,
                'days_before_expiry': 2,
                'base_coins': 250,
                'streak_coins': 500,
                'streak_threshold': 7,
                'expired_reason': 'one day'
            },
            'weekly': {
                'collected':    enums.Updateable.WEEKLY_COLLECTED,
                'streak':       enums.Updateable.WEEKLY_STREAK,
                'days_before_claimable': 7,
                'days_before_expiry': 14,
                'base_coins':   1500,
                'streak_coins': 3000,
                'streak_threshold': 4,
                'expired_reason': 'one week'
            },
            'monthly': {
                'collected':    enums.Updateable.MONTHLY_COLLECTED,
                'streak':       enums.Updateable.MONTHLY_STREAK,
                'days_before_claimable': 30,
                'days_before_expiry': 60,
                'base_coins':   5000,
                'streak_coins': 10000,
                'streak_threshold': 3,
                'expired_reason': 'one month (30 days)'
            }
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        if await self.bot.redis.exists(f'{message.author.id}_xp_gain') is True:
            return

        user_config = await self.bot.user_manager.get_or_create_config(user_id=message.author.id)

        xp = random.randint(10, 25)

        if xp >= user_config.next_level_xp:
            self.bot.dispatch('xp_level_up', user_config)

        await self.bot.user_manager.set_xp(user_id=message.author.id, xp=xp)
        await self.bot.redis.setex(name=f'{message.author.id}_xp_gain', time=60, value=None)

    @commands.Cog.listener()
    async def on_xp_level_up(self, user_config: objects.UserConfig) -> None:
        pass

        # TODO Implement notifications stuff.

        """
        user = self.bot.get_user(id=user_id)
        try:
            await user.send(f'Congrats, you are now level `{user_config.level}`!')
        
        except discord.Forbidden:
            return
        """

    #

    @commands.command(name='claim')
    async def claim(self, ctx: context.Context, claim: Literal['daily', 'weekly', 'monthly'] = 'daily') -> None:
        """
        Claim a daily, weekly or monthly coin bundle.

        `claim`: The type of bundle to claim, can be `daily`, `weekly` or `monthly`.
        """

        user_config = await self.bot.user_manager.get_or_create_config(user_id=ctx.author.id)
        now = pendulum.now(tz='UTC')

        time_when_claimable = getattr(user_config, self.claims[claim]['collected'].value).add(days=self.claims[claim]['days_before_claimable'])
        if now < time_when_claimable:
            time_difference = utils.format_difference(datetime=time_when_claimable, suppress=[])
            raise exceptions.ArgumentError(f'Your `{claim}` bundle is currently on cooldown. Retry the command in `{time_difference}`.')

        coins = self.claims[claim]['base_coins']

        embed = discord.Embed(
                colour=ctx.colour, title=f'{claim.title()} bundle claim:',
                description=f'You gained `{coins}` coins for claiming your `{claim.title()}` bundle!\n\n'
        )

        time_when_streak_expires = getattr(user_config, self.claims[claim]['collected'].value).add(days=self.claims[claim]['days_before_expiry'])
        if now < time_when_streak_expires:

            if getattr(user_config, self.claims[claim]['streak'].value) + 1 >= self.claims[claim]['streak_threshold']:
                await self.bot.user_manager.set_bundle_streak(user_id=ctx.author.id, type=self.claims[claim]['streak'], operation=enums.Operation.RESET)
                embed.description += f'You were awarded an extra `{self.claims[claim]["streak_coins"] - self.claims[claim]["base_coins"]}` coins for maintaining your ' \
                                     f'`{claim.title()}` streak which has now been reset to 0.\n\n'
            else:
                await self.bot.user_manager.set_bundle_streak(user_id=ctx.author.id, type=self.claims[claim]['streak'], operation=enums.Operation.ADD, count=1)
                embed.description += f'You are now on a `{getattr(user_config, self.claims[claim]["streak"].value)}` out of `{self.claims[claim]["streak_threshold"]}` ' \
                                     f'`{claim.title()}` streak.\n\n'

        else:

            await self.bot.user_manager.set_bundle_streak(user_id=ctx.author.id, type=self.claims[claim]['streak'], operation=enums.Operation.RESET)
            embed.description += f'Your `{claim.title()}` streak is over because you didnt claim your bundle within {self.claims[claim]["expired_reason"]} of the last claim.'

        await self.bot.user_manager.set_coins(user_id=ctx.author.id, coins=coins)
        await self.bot.user_manager.set_bundle_collection(user_id=ctx.author.id, type=self.claims[claim]['collected'])
        await ctx.send(embed=embed)

    #

    @commands.command(name='profile')
    async def profile(self, ctx: context.Context, member: discord.Member = None) -> None:
        """
        Display information about yours, or someone else's profile.

        `member`: The member of which to get the profile for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        user_config = self.bot.user_manager.get_config(user_id=member.id)

        embed = discord.Embed(
                colour=user_config.colour, title=f'{member}\'s profile',
                description=f'`Total xp:` {user_config.xp}\n'
                            f'`Next level xp:` {user_config.next_level_xp}\n'
                            f'`Level:` {user_config.level}\n'
                            f'`Coins:` {user_config.coins}\n'
                            f'`Rank (server):` {self.bot.user_manager.rank(user_id=member.id, guild_id=ctx.guild.id)}\n'
                            f'`Rank (global):` {self.bot.user_manager.rank(user_id=member.id)}'
        )
        await ctx.send(embed=embed)

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx: context.Context, type: Literal['xp', 'level', 'coins'] = 'xp') -> None:
        """
        Display the leaderboard for xp, coins or level in the current server.

        `type`: The type of leaderboard to show, could be `xp`, `level` or `coins`
        """

        leaderboard = self.bot.user_manager.leaderboard(type=type, guild_id=ctx.guild.id)
        if not leaderboard:
            raise exceptions.ArgumentError(f'There are no leaderboard stats.')

        entries = [
            f'{index + 1:<6} |{getattr(user_config, type):<10} |{ctx.bot.get_user(user_id)}'
            for index, (user_id, user_config) in enumerate(leaderboard)
        ]

        title = f'`{type.title()}` leaderboard in `{ctx.guild}`:'
        header = f'Rank   |{type.title():<10} |Name\n'
        await ctx.paginate_embed(entries=entries, per_page=10, title=title, header=header, codeblock=True)

    @commands.command(name='global-leaderboard', aliases=['glb'])
    async def global_leaderboard(self, ctx: context.Context, type: Literal['xp', 'level', 'coins'] = 'xp') -> None:
        """
        Display the global leaderboard for xp, coins or level.

        `type`: The type of leaderboard to show, could be `xp`, `level` or `coins`
        """

        leaderboard = self.bot.user_manager.leaderboard(type=type)
        if not leaderboard:
            raise exceptions.ArgumentError(f'There are no leaderboard stats.')

        entries = [
            f'{index + 1:<6} |{getattr(user_config, type):<10} |{ctx.bot.get_user(user_id)}'
            for index, (user_id, user_config) in enumerate(leaderboard)
        ]

        title = f'`{type.title()}` leaderboard across the whole bot.'
        header = f'Rank   |{type.title():<10} |Name\n'
        await ctx.paginate_embed(entries=entries, per_page=10, title=title, header=header, codeblock=True)

    #

    @commands.command(name='rank', aliases=['r'])
    async def rank(self, ctx: context.Context, member: Optional[discord.Member]) -> None:
        """
        Displays yours, or someone else's rank in the current server.

        `member`: The member of which to get the rank for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        rank = self.bot.user_manager.rank(user_id=member.id, guild_id=ctx.guild.id)
        await ctx.send(f'`{member}` is rank `{rank}` in this server.')

    @commands.command(name='global-rank', aliases=['gr'])
    async def global_rank(self, ctx: context.Context, member: Optional[discord.Member]) -> None:
        """
        Displays yours, or someone else's rank in the current server.

        `member`: The member of which to get the rank for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        rank = self.bot.user_manager.rank(user_id=member.id)
        await ctx.send(f'`{member}` is rank `{rank}` across the whole bot.')

    #

    @commands.command(name='coins', aliases=['money', 'cash'])
    async def coins(self, ctx: context.Context, member: discord.Member = None) -> None:
        """
        Display how many coins you or someone else has.

        `member`: The member of which to get the amount of coins for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        await ctx.send(f'{member} has `{self.bot.user_manager.get_config(user_id=member.id).coins}` coins.')

    @commands.command(name='xp')
    async def xp(self, ctx: context.Context, member: discord.Member = None) -> None:
        """
        Display how much xp you or someone else has.

        `member`: The member of which to get the amount of xp for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        await ctx.send(f'{member} has `{self.bot.user_manager.get_config(user_id=member.id).xp}` xp.')

    @commands.command(name='level')
    async def level(self, ctx: context.Context, member: discord.Member = None) -> None:
        """
        Display yours, or someone else's level.

        `member`: The member of which to get the level for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        await ctx.send(f'{member} is level `{self.bot.user_manager.get_config(user_id=member.id).level}`.')


def setup(bot: Life):
    bot.add_cog(Economy(bot))
