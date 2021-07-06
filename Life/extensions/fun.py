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

import logging
import asyncio
import random

import discord
from discord.ext import commands

from core import colours
from core.emojis import CROSS
from utilities.context import Context

__log__: logging.Logger = logging.getLogger("cogs.fun")
  
def setup(bot: Life) -> None:
    bot.add_cog(Todo(bot))
    
class Fun(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot
        
    @commands.command()
    async def rps(self, ctx: Context):
        REACTIONS = ['\U0001faa8', '\U0001f4f0', '\U00002702']
		MYCHOICE  = random.choice(["\U0001faa8", "\U0001f4f0", "\U00002702"])

		LOSE = 'You won!, GG'
		WIN  = 'I won!, GG'
		DRAW = 'We both picked the same, It\'s a draw!'

		msg = await ctx.reply('Let\'s see who wins!')
		for reaction in REACTIONS: await msg.add_reaction(reaction)
		try:
			reaction, user = await self.bot.wait_for(event   = 'reaction_add', 
								 timeout = 45.0, 
								 check   = lambda reaction, user: reaction.message.id == msg.id and user.id == ctx.author.id and reaction.emoji in REACTIONS)
		except asyncio.TimeoutError: return await ctx.reply(f"{CROSS} | **Timed out:** You took too long to respond! **[45s]**")

		if (CHOICE := reaction.emoji) == '\U0001faa8':
			if CHOICE == MYCHOICE: await msg.edit(content = DRAW)
			elif MYCHOICE == '\U0001f4f0': await msg.edit(content = WIN)
			elif MYCHOICE == '\U00002702': await msg.edit(content = LOSE) 
		elif (CHOICE := reaction.emoji) == '\U0001f4f0':
			if CHOICE == MYCHOICE: await msg.edit(content = DRAW)
			elif MYCHOICE == '\U00002702': await msg.edit(content = WIN)
			elif MYCHOICE == '\U0001faa8': await msg.edit(content = LOSE) 
		elif (CHOICE := reaction.emoji) == '\U00002702':
			if CHOICE == MYCHOICE: await msg.edit(content = DRAW)
			elif MYCHOICE == '\U0001faa8': await msg.edit(content = WIN)
			elif MYCHOICE == '\U0001f4f0': await msg.edit(content = LOSE)
			
	@commands.command()
	async def gayrate(self, ctx: Context, member: discord.Member = None):
		if member is None: member = ctx.author
		return await ctx.reply(embed=discord.Embed(description = f"**{member.name}** is {random.randint(10, 100)}", colour=colours.MAIN))
	
	@commands.command()
	async def iqrate(self, ctx: Context, member: discord.Member = None):
		if member is None: member = ctx.author
		return await ctx.reply(embed=discord.Embed(description = f"**{member.name}'s** IQ is **{random.randint(40, 150)}** :nerd:", colour=colours.MAIN))
        
