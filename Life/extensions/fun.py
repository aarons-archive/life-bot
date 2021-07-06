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

import asyncio
import logging
import random
from typing import Optional

import discord
from discord.ext import commands

from core import colours, emojis
from core.bot import Life
from utilities import context, exceptions, utils


__log__: logging.Logger = logging.getLogger("cogs.fun")


class Fun(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.command(name="rps")
    async def rps(self, ctx: context.Context) -> None:
        """
        Play rock, paper, scissors with the bot.
        """

        REACTIONS = ["\U0001faa8", "\U0001f4f0", "\U00002702"]
        MY_CHOICE = random.choice(['\U0001faa8', '\U0001f4f0', '\U00002702'])

        LOSE = "You won!, GG"
        WIN = "I won!, GG"
        DRAW = "We both picked the same, It's a draw!"

        message = await ctx.reply("Let's see who wins!")
        for reaction in REACTIONS:
            await message.add_reaction(reaction)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=45.0, check=lambda r, u: r.message.id == message.id and u.id == ctx.author.id and r.emoji in REACTIONS)
        except asyncio.TimeoutError:
            raise exceptions.EmbedError(emoji=emojis.CROSS, colour=colours.RED, description="You took too long to respond!")

        if (choice := reaction.emoji) == "\U0001faa8":
            if choice == MY_CHOICE:
                await message.edit(content=DRAW)
            elif MY_CHOICE == "\U0001f4f0":
                await message.edit(content=WIN)
            elif MY_CHOICE == "\U00002702":
                await message.edit(content=LOSE)

        elif (choice := reaction.emoji) == "\U0001f4f0":
            if choice == MY_CHOICE:
                await message.edit(content=DRAW)
            elif MY_CHOICE == "\U00002702":
                await message.edit(content=WIN)
            elif MY_CHOICE == "\U0001faa8":
                await message.edit(content=LOSE)

        elif (choice := reaction.emoji) == "\U00002702":
            if choice == MY_CHOICE:
                await message.edit(content=DRAW)
            elif MY_CHOICE == "\U0001faa8":
                await message.edit(content=WIN)
            elif MY_CHOICE == "\U0001f4f0":
                await message.edit(content=LOSE)

    @commands.command(name="gayrate", aliases=["gay-rate", "gay_rate"])
    async def gay_rate(self, ctx: context.Context, member: Optional[discord.Member]) -> None:
        """
        See how gay you, or someone else is.
        """

        person: discord.Member = member or ctx.author
        await ctx.reply(embed=utils.embed(description=f'**{person.name}** is **{random.randint(10, 100)}%** gay :rainbow:'))

    @commands.command(name="iqrate", aliases=["iq-rate", "iq_rate"])
    async def iq_rate(self, ctx: context.Context, member: Optional[discord.Member]) -> None:
        """
        See yours, or someone else's IQ.
        """

        person: discord.Member = member or ctx.author
        await ctx.reply(embed=utils.embed(description=f"**{person.name}'s** IQ is **{random.randint(40, 150)}**  :nerd:"))


def setup(bot: Life) -> None:
    bot.add_cog(Fun(bot))
