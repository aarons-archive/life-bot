from discord.ext import commands


class Accounts(commands.Cog):
    """
    Account commands.
    """

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Accounts(bot))
