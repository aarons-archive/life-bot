from .objects.account import Account


class Manager:

    def __init__(self, bot):
        self.bot = bot

    def get_account(self, account_id):
        return self.bot.accounts.get(account_id)

    async def fetch_account(self, account_id):
        # Fetch user from database
        account = await self.bot.db.fetch("SELECT * FROM accounts where id = $1", account_id)
        items = await self.bot.db.fetch("SELECT * FROM inventory where owner = $1", account_id)

        # Return an account object
        return Account(dict(account[0]), items)

    def get_item(self, account_id, item_id):
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

    async def fetch_item(self, account_id, item_id):
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







