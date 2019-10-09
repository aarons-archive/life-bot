from .objects.account import Account
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
            await self.bot.db.execute(f"INSERT INTO accounts VALUES ($1, 'bg_default', 1000, 1000, 0)", user_id)

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
            return self.bot.accounts.get(account_id)
        # Return none if no account was found.
        except ValueError:
            return None

    async def fetch_account(self, account_id):
        try:
            # Fetch user from database.
            account = await self.bot.db.fetch("SELECT * FROM accounts where id = $1", account_id)
            items = await self.bot.db.fetch("SELECT * FROM inventory where owner = $1", account_id)
            # Return an account object.
            return Account(dict(account[0]), items)
        # Return none if no account was found.
        except ValueError:
            return None

    def get_item_id(self, account_id, item_id):
        # Get the account with the given id.
        account = self.get_account(account_id)
        # If no account was found.
        if not account:
            return None
        # Get all items with the given id.
        items = [item for item in account.inventory if item["id"] == item_id]
        # If no items where found.
        if not items:
            return None
        # Define a list for the nonstackable items.
        non_stackables = []
        # Loop through items.
        for item in items:
            # If the item is not stackable, add it to a list.
            if item["stackable"] is False:
                non_stackables.append(item)
            # If the item is stackable, return it since there will only be one.
            else:
                return item
        # Return any non_stackables.
        return non_stackables

    async def fetch_item_id(self, account_id, item_id):
        # Get the account with the given id.
        account = await self.fetch_account(account_id)
        # If no account was found.
        if not account:
            return None
        # Get all items with the given id.
        items = [item for item in account.inventory if item["id"] == item_id]
        # If no items where found.
        if not items:
            return None
        # Define a list for the non stackable items.
        non_stackables = []
        # Loop through items.
        for item in items:
            # If the item is not stackable, add it to a list.
            if item["stackable"] is False:
                non_stackables.append(item)
            # If the item is stackable, return it since there will only be one.
            else:
                return item
        # Return any non_stackables.
        return non_stackables

    def get_item_type(self, account_id, item_type):
        # Get the account with the given id.
        account = self.get_account(account_id)
        # If no account was found.
        if not account:
            return None
        # Get all items with the given id.
        items = [item for item in account.inventory if item["type"] == item_type]
        # If no items where found.
        if not items:
            return None
        # Return items
        return items

    async def fetch_item_type(self, account_id, item_type):
        # Get the account with the given id.
        account = await self.fetch_account(account_id)
        # If no account was found.
        if not account:
            return None
        # Get all items with the given id.
        items = [item for item in account.inventory if item["type"] == item_type]
        # If no items where found.
        if not items:
            return None
        # Return items.
        return items








