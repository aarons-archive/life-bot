from cogs.rpg.objects.inventory import Inventory


class Account:

    def __init__(self, account, items):

        self.inventory = Inventory(items)
        self.items = self.inventory.items
        self.raw_items = self.inventory.raw_items

        self.raw_account = account

        self.id = account.get("id", 0)
        self.cash = account.get("cash", 0)
        self.bank = account.get("bank", 0)
        self.level = account.get("level", 0)

    def __repr__(self):
        return f"<Account id={self.id} cash={self.cash} bank={self.bank} level={self.level}>"
