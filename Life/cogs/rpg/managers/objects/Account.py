from .Inventory import Inventory


class Account:

    def __init__(self, data, raw_inventory):

        self.inventory_manager = Inventory(raw_inventory)

        self.raw_inventory = self.inventory_manager.raw_inventory
        self.inventory = self.inventory_manager.inventory

        self.primary_weapon = self.inventory_manager.get_item_slot("Primary")
        self.secondary_weapon = self.inventory_manager.get_item_slot("Secondary")
        self.power_weapon = self.inventory_manager.get_item_slot("Power")
        self.helmet = self.inventory_manager.get_item_slot("Helmet")
        self.cloak = self.inventory_manager.get_item_slot("Cloak")
        self.boots = self.inventory_manager.get_item_slot("Boots")

        self.id = data.get("id", 0)
        self.cash = data.get("cash", 0)
        self.bank = data.get("bank", 0)
        self.level = (self.primary_weapon.power + self.secondary_weapon.power + self.power_weapon.power + self.helmet.power + self.cloak.power + self.boots.power) / 6

    def __repr__(self):
        return "<Account id={0.id} cash={0.cash} bank={0.bank} level={0.level}".format(self)
