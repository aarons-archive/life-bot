from discord.ext import commands


class Images(commands.Cog):
    """
    Image manipulation commands.
    """

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Images(bot))
