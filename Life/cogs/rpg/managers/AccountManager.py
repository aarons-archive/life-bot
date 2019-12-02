import asyncpg

from cogs.rpg.objects import Account


class AccountManager:

    def __init__(self, bot):
        self.bot = bot

    async def cache_accounts(self):

        self.bot.accounts = {}

        accounts = await self.bot.db.fetch("SELECT * FROM accounts")

        for account in accounts:
            items = await self.bot.db.fetch("SELECT * FROM inventory WHERE owner = $1", account["id"])
            self.bot.accounts[account["id"]] = Account(dict(account), items)

        print(f"\n[RPG] Successfully cached {len(accounts)} accounts.")

    async def cache_account(self, account_id):

        account = await self.fetch_account(account_id)

        if account:
            self.bot.accounts[account.id] = account

        return account

    def get_account(self, account_id):

        try:
            return self.bot.accounts.get(account_id)
        except ValueError:
            return None

    async def fetch_account(self, account_id):

        try:
            account = await self.bot.db.fetch("SELECT * FROM accounts where id = $1", account_id)
            items = await self.bot.db.fetch("SELECT * FROM inventory where owner = $1", account_id)
            return Account(dict(account[0]), items)
        except ValueError:
            return None

    async def create_account(self, ctx, user_id):
        try:
            await self.bot.db.execute(f"INSERT INTO accounts VALUES ($1, 'bg_default', 1000, 1000)", user_id)

            await self.cache_account(user_id)

            return await ctx.send(f"Account created with ID `{user_id}`")

        except asyncpg.UniqueViolationError:
            return await ctx.send("You already have an account.")

    async def delete_account(self, ctx, user_id):

        account = self.get_account(user_id)
        if not account:
            return await ctx.send("You don't have an account.")

        await self.bot.db.execute(f"DELETE FROM accounts WHERE id = $1", user_id)
        self.bot.accounts.pop(user_id, None)

        return await ctx.send("Deleted your account.")
