from discord.ext import commands


class Accounts(commands.Cog):
    """
    Account commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create")
    async def create(self, ctx):
        """
        Create an account
        """
        return await self.bot.account_manager.create_account(ctx, ctx.author.id)

    @commands.command(name="delete")
    async def delete(self, ctx):
        """
        Delete your account.
        """
        return await self.bot.account_manager.delete_account(ctx, ctx.author.id)


def setup(bot):
    bot.add_cog(Accounts(bot))
