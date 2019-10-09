from discord.ext import commands
import discord


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

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx):

        # Get the users account.
        account = self.bot.account_manager.get_account(ctx.author.id)

        # If no account was found return.
        if not account:
            return await ctx.send(f"You don't have an account. Use `{ctx.prefix}create` to make one.")

        if not account.inventory:
            return await ctx.send("You don't have any items.")

        # Create an embed.
        embed = discord.Embed(
            title=f"{ctx.author}'s Inventory:",
            description=f"",
            colour=discord.Color.gold()
        )
        embed.set_footer(text=f"ID: {account.id}")
        for item in account.inventory:
            embed.description += f"{item['name']} - Id: {item['id']}\n"

        # Send the embed.
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Accounts(bot))
