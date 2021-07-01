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

import functools
import random
import textwrap
from typing import Optional

import discord
from discord.ext import commands

import objects
from core.bot import Life
from utilities import context, exceptions, utils


class Economy(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        if await self.bot.redis.exists(f'{message.author.id}_xp_gain') is True:
            return

        user_config = await self.bot.user_manager.get_or_create_config(message.author.id)

        xp = random.randint(10, 25)

        if xp >= user_config.next_level_xp:
            self.bot.dispatch('xp_level_up', message, user_config)

        user_config.change_xp(xp)
        await self.bot.redis.setex(name=f'{message.author.id}_xp_gain', time=60, value='')

    @commands.Cog.listener()
    async def on_xp_level_up(self, message: discord.Message, user_config: objects.UserConfig) -> None:

        if not user_config.notifications.level_ups:
            return

        await message.reply(f'You are now level `{user_config.level}`!')

    #

    @commands.command(name='level', aliases=['xp', 'score', 'rank'], ignore_extra=False)
    async def level(self, ctx: context.Context, member: Optional[discord.Member]) -> None:
        """
        Display yours, or someone else's level / xp information.

        `member`: The member of which to get the level for. Can be their ID, Username, Nickname or @Mention. Defaults to you.
        """

        if not member:
            member = ctx.author

        async with ctx.typing():
            file = await self.bot.user_manager.create_level_card(member.id, guild_id=getattr(ctx.guild, 'id', None))
            await ctx.reply(file=file)

    @commands.group(name='leaderboard', aliases=['lb'], invoke_without_command=True)
    async def leaderboard(self, ctx: context.Context) -> None:
        """
        Display the leaderboard for xp, rank, and level.
        """

        leaderboards = (len(self.bot.user_manager.leaderboard(guild_id=getattr(ctx.guild, 'id', None))) // 10) + 1

        entries = [functools.partial(self.bot.user_manager.create_leaderboard, guild_id=getattr(ctx.guild, 'id', None)) for _ in range(leaderboards)]
        await ctx.paginate_file(entries=entries)

    @leaderboard.command(name='text')
    async def leaderboard_text(self, ctx: context.Context) -> None:
        """
        Display the xp leaderboard in a text table.
        """

        if not (leaderboard := self.bot.user_manager.leaderboard()):
            raise exceptions.ArgumentError('There are no leaderboard stats.')

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        header = textwrap.dedent(
                '''
                ╔═══════╦═══════════╦═══════╦═══════════════════════════════════════╗
                ║ Rank  ║ XP        ║ Level ║ Name                                  ║
                ╠═══════╬═══════════╬═══════╬═══════════════════════════════════════╣
                '''
        )

        footer = textwrap.dedent(
                f'''
                ║       ║           ║       ║                                       ║
                ║ {self.bot.user_manager.rank(ctx.author.id):<5} ║ {user_config.xp:<9} ║ {user_config.level:<5} ║ {str(ctx.author):<37} ║
                ╚═══════╩═══════════╩═══════╩═══════════════════════════════════════╝
                '''
        )

        # noinspection PyTypeChecker
        entries = [
            f'║ {index + 1:<5} ║ {user_config.xp:<9} ║ {user_config.level:<5} ║ {utils.name(person=self.bot.get_user(user_config.id), guild=ctx.guild):<37} ║'
            for index, user_config in enumerate(leaderboard)
        ]

        await ctx.paginate(entries=entries, per_page=10, header=header, footer=footer, codeblock=True)


def setup(bot: Life) -> None:
    bot.add_cog(Economy(bot=bot))
