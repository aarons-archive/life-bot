import discord
from discord.ext import commands

from core.bot import Life

def setup(bot: Life) -> None:
  bot.add_cog(Colors(bot=bot))

class Colors(commands.Cog) -> None:
  
  def __init__(self, bot: Life):
    self.bot = bot
