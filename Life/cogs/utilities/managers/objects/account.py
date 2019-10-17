from .Inventory import Inventory


class Account:

    def __init__(self, data, raw_inventory):

        self.inventory_manager = Inventory(raw_inventory)

        self.id = data.get("id", 0)
        self.cash = data.get("cash", 0)
        self.bank = data.get("bank", 0)

        self.raw_inventory = self.inventory_manager.raw_inventory
        self.inventory = self.inventory_manager.inventory

    def __repr__(self):
        return "<Account id={0.id} cash={0.cash} bank={0.bank} inventory={0.inventory}>".format(self)
