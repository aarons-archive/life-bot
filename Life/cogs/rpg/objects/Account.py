from cogs.rpg.managers.InventoryManager import InventoryManager

class Account:

    def __init__(self, data, raw_inventory):

        self.InventoryManager = InventoryManager(raw_inventory)

        self.inventory = self.InventoryManager.inventory
        self.raw_inventory = raw_inventory

        self.id = data.get("id", 0)
        self.cash = data.get("cash", 0)
        self.bank = data.get("bank", 0)
        self.level = "PLACHOLDER"

    def __repr__(self):
        return "<Account id={0.id} cash={0.cash} bank={0.bank} level={0.level}>".format(self)
