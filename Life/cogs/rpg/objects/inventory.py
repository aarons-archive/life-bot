from .boots import *
from .chestplate import *
from .helmet import *

item_list = {
    1: StarterBoots,
    101: StarterChestplate,
    201: StarterHelmet
}


class Inventory:

    def __init__(self, raw_inventory: list):

        self.raw = raw_inventory
        self.items = self.get_inventory_objects(self.raw)

    def get_inventory_objects(self, items: list):

        inventory = []

        for item in items:
            item_object = item_list.get(item["id"], None)
            if not item_object:
                continue
            inventory.append(item_object(item))

        return inventory

    def get_item_id(self, item_id: int):

        items_of_id = [item for item in self.items if item.id == item_id]

        if not items_of_id:
            return None

        elif len(items_of_id) == 1:
            return items_of_id[0]

        else:
            return items_of_id

    def get_item_slot(self, item_slot: str):

        items_of_slot = [item for item in self.items if item.slot == item_slot]

        if not items_of_slot:
            return None

        elif len(items_of_slot) == 1:
            return items_of_slot[0]

        else:
            return items_of_slot

    def get_item_base_type(self, item_base_type: str):

        items_of_base_type = [item for item in self.items if item.base_type == item_base_type]

        if not items_of_base_type:
            return None

        elif len(items_of_base_type) == 1:
            return items_of_base_type[0]

        else:
            return items_of_base_type

    def get_item_type(self, item_type: str):

        items_of_type = [item for item in self.items if item.type == item_type]

        if not items_of_type:
            return None

        elif len(items_of_type) == 1:
            return items_of_type[0]

        else:
            return items_of_type

