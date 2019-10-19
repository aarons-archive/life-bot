from .PrimaryWeapons import *
from .SecondaryWeapons import *
from .PowerWeapons import *
from .Helmet import *
from .Cloak import *
from .Boots import *

items = {
    1: Glock19,
    101: MP5,
    201: Bazooka,
    301: StarterHelmet,
    401: StarterCloak,
    501: StarterBoots,
}


class Items:

    @staticmethod
    def get_item(item):
        item_object = items.get(item["id"], None)
        if item_object is None:
            return None
        return item_object(item)


class Inventory:

    def __init__(self, raw_inventory):

        self.item_manager = Items()

        self.raw_inventory = raw_inventory
        self.inventory = [self.item_manager.get_item(item) for item in self.raw_inventory]

    def get_item_slot(self, slot):
        for item in self.inventory:
            if item.slot == slot:
                return item

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
                non_stackables.append(item)

        # Return the non-stackable items.
        return non_stackables

    def get_item_type(self, item_type):
        # If the account has no items.
        if not self.inventory:
            return None

        # Define a list of items of the type to return.
        items_of_type = []

        # Loop through the items.
        for item in self.inventory:

            # If the items id is equal to the one the user wants to get.
            if item.type == item_type:

                # Append the items to the list.
                items_of_type.append(item)

        # Return the items.
        if len(items_of_type) == 1:
            return items_of_type[0]
        else:
            return items_of_type

    def get_item_name(self, item_name):
        # If the account has no items.
        if not self.inventory:
            return None

        # Define a list of items of the type to return.
        items_of_name = []

        # Loop through the items.
        for item in self.inventory:

            # If the items id is equal to the one the user wants to get.
            if item.base_name == item_name:

                # Append the items to the list.
                items_of_name.append(item)

        # Return the items.
        # Return the items.
        if len(items_of_name) == 1:
            return items_of_name[0]
        else:
            return items_of_name

