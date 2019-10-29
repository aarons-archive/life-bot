from .PrimaryWeapons import *
from .SecondaryWeapons import *
from .PowerWeapons import *
from .Helmets import *
from .Cloaks import *
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
        self.inventory = [self.item_manager.get_item(dict(item)) for item in self.raw_inventory]

    def get_item_slot(self, item_slot):
        items_of_slot = [item for item in self.inventory if item.slot == item_slot]
        if len(items_of_slot) > 0:
            return items_of_slot[0]
        else:
            return None

    def get_item_id(self, item_id):

        # Get all items with the given id.
        items_of_id = [item for item in self.inventory if item.id == item_id]

        # If no items were found, return None.
        if not items_of_id:
            return None

        # If there is more then 1 item, return the list.
        if len(items_of_id) > 1:
            return items_of_id
        # Otherwise return just the 1st item in the list.
        else:
            return items_of_id[0]

    def get_item_sub_type(self, item_sub_type):

        # Get all items with the given sub_type.
        items_of_id = [item for item in self.inventory if item.base_type == item_sub_type]

        # If no items were found, return None.
        if not items_of_id:
            return None

        # If there is more then 1 item, return the list.
        if len(items_of_id) > 1:
            return items_of_id
        # Otherwise return just the 1st item in the list.
        else:
            return items_of_id[0]

    def get_item_type(self, item_type):

        # Get all items with the given type.
        items_of_id = [item for item in self.inventory if item.type == item_type]

        # If no items were found, return None.
        if not items_of_id:
            return None

        # If there is more then 1 item, return the list.
        if len(items_of_id) > 1:
            return items_of_id
        # Otherwise return just the 1st item in the list.
        else:
            return items_of_id[0]

    def get_item_base_name(self, item_base_name):

        # Get all items with the given base_name.
        items_of_id = [item for item in self.inventory if item.base_name == item_base_name]

        # If no items were found, return None.
        if not items_of_id:
            return None

        # If there is more then 1 item, return the list.
        if len(items_of_id) > 1:
            return items_of_id
        # Otherwise return just the 1st item in the list.
        else:
            return items_of_id[0]

    def get_item_name(self, item_name):

        # Get all items with the given name.
        items_of_id = [item for item in self.inventory if item.name == item_name]

        # If no items were found, return None.
        if not items_of_id:
            return None

        # If there is more then 1 item, return the list.
        if len(items_of_id) > 1:
            return items_of_id
        # Otherwise return just the 1st item in the list.
        else:
            return items_of_id[0]
