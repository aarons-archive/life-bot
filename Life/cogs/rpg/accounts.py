import discord
from discord.ext import commands, flags

from cogs.rpg.managers.AccountManager import AccountManager


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

        await self.bot.account_manager.cache_accounts()

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

    @commands.command(name="account", aliases=["profile"])
    async def account(self, ctx, member: discord.Member = None):

        if not member:
            member = ctx.author

        account = self.bot.account_manager.get_account(member.id)
        if not account:
            return await ctx.send(f"Either you or the target does not have an account.")

        embed = discord.Embed(
            colour=discord.Colour.gold(),
            title=f"**{member.name}'s profile:**\n"
        )
        embed.set_author(icon_url=ctx.author.avatar_url_as(format="png"), name=ctx.author.name)
        embed.set_footer(text=f"ID: {account.id}")
        # TODO: Finish adding stuff to profile.
        embed.description = f"**Money:**\nBank: {account.bank}\nCash: {account.cash}"

        return await ctx.send(embed=embed)

    @flags.add_flag("--id", type=int, default=None)
    @flags.add_flag("--slot", type=str, default=None)
    @flags.add_flag("--basename", type=str, default=None)
    @flags.add_flag("--name", type=str, default=None)
    @flags.add_flag("--basetype", type=str, default=None)
    @flags.add_flag("--type", type=str, default=None)
    @flags.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx, **options):

        account = ctx.account
        if not account:
            return await ctx.send(f"You don't have an account")

        account_items = account.items.copy()
        if not account_items:
            return await ctx.send("You don't have any items in your inventory.")

        searches = {
            "id": account.inventory.get_item_id,
            "slot": account.inventory.get_item_slot,
            "basename": account.inventory.get_item_base_name,
            "name": account.inventory.get_item_name,
            "basetype": account.inventory.get_item_base_type,
            "type": account.inventory.get_item_type
        }

        for option, value in options.items():

            if value is None:
                continue

            search_items = searches[option](account_items, value)
            if not search_items:
                account_items.clear()

            account_items = [item for item in account_items if item in search_items]

        if not account_items:
            return await ctx.send("You have no items which match all of your search options.")

        def key(e):
            return e.name

        entries = []
        for item in sorted(account_items, key=key):
            message = f"Information about **{item.name}**:\n" \
                      f"**ID:** {item.id}\n" \
                      f"**Power:** {item.power}\n" \
                      f"**Current slot:** {item.slot.title()}\n" \
                      f"**Base Name:** {item.base_name.title()}\n" \
                      f"**Base type:** {item.base_type.title()}\n" \
                      f"**Type:** {item.type.title()}\n"
            entries.append(message)

        return await ctx.paginate_embed(entries=entries, entries_per_page=3)

def setup(bot):
    bot.add_cog(Accounts(bot))
