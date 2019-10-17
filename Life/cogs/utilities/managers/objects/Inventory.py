from .PrimaryWeapons import *
from .SecondaryWeapons import *
from .PowerWeapons import *

items = {
    1: Pistol,
    101: SubmachineGun,
    201: RocketLauncher,
}


class Items:

    def get_item(self, item):
        item_object = items.get(item["id"], None)
        if item_object is None:
            return None
        else:
            return item_object(item)


class Inventory:

    def __init__(self, raw_inventory):

        self.item_manager = Items()

        self.raw_inventory = raw_inventory
        self.inventory = [self.item_manager.get_item(item) for item in self.raw_inventory]

    def get_item_id(self, item_id):

        # If the account has no items.
        if not self.inventory:
            return None

        # Define a list for if the item we want to find is non-stackable.
        non_stackables = []

        # Loop through the items.
        for item in self.inventory:

            # If the items id is equal to the one the user wants to get.
            if item.id == item_id:

                # And the item is stackable.
                if item.stackable:
                    # Return it.
                    return item

                # If the item is non-stackable, add it to the list to return later.
                else:
                    non_stackables.append(item)

        # Return the non-stackable items.
        return non_stackables
