from discord.ext import commands

from Life.Life.cogs.rpg.managers import AccountManager


class Accounts(commands.Cog):
    """
    Account commands.
    """

    def __init__(self, bot):
        self.bot = bot

        self.bot.account_manager = AccountManager(self.bot)
        self.bot.accounts = {}

    @commands.Cog.listener()
    async def on_ready(self):

        # Fetch players from the database, and cache them.
        await self.bot.account_manager.cache_all_accounts()

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
