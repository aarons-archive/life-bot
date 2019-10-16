from .objects import Account
import asyncpg


class AccountManager:

    def __init__(self, bot):
        self.bot = bot

    async def cache_all_accounts(self):
        # Fetch all accounts from the database
        accounts = await self.bot.db.fetch("SELECT * FROM accounts")

        # Loop through the accounts.
        for account in accounts:

            # Fetch the accounts items from the database.
            items = await self.bot.db.fetch("SELECT * FROM inventory WHERE owner = $1", account["id"])

            # Add the account to the cache.
            self.bot.accounts[account["id"]] = Account(dict(account), items)

    async def cache_account(self, account_id):
        # Fetch the account from the database.
        account = await self.fetch_account(account_id)

        # If an account was found.
        if account:

            # Add the account to the cache.
            self.bot.accounts[account.id] = account

    async def create_account(self, ctx, user_id):
        try:
            # Add the account to the database.
            await self.bot.db.execute(f"INSERT INTO accounts VALUES ($1, 'bg_default', 1000, 1000)", user_id)

            # Cache the account.
            await self.cache_account(user_id)

            # Account creation was successful.
            return await ctx.send(f"Account created with ID `{user_id}`")

        # Accept an error if they already have an account.
        except asyncpg.UniqueViolationError:
            return await ctx.send("You already have an account.")

    async def delete_account(self, ctx, user_id):
        # Check if the user has an account.
        account = self.get_account(user_id)
        if not account:
            return await ctx.send("You don't have an account.")

        # The user has an account, so delete it.
        await self.bot.db.execute(f"DELETE FROM accounts WHERE id = $1", user_id)
        self.bot.accounts.pop(user_id, None)
        await ctx.send("Deleted your account.")

    def get_account(self, account_id):
        try:
            # Get account from local cache.
            return self.bot.accounts.get(account_id)
        except ValueError:
            # Return none if no account was found.
            return None

    async def fetch_account(self, account_id):
        try:
            # Fetch user from database.
            account = await self.bot.db.fetch("SELECT * FROM accounts where id = $1", account_id)
            items = await self.bot.db.fetch("SELECT * FROM inventory where owner = $1", account_id)
            # Return an account object.
            return Account(dict(account[0]), items)

        except ValueError:
            # Return None if no account was found.
            return None
