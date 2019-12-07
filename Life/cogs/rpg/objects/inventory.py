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

    def get_item_slot(self, slot: str):

        items_of_slot = [item for item in self.items if item.slot == slot]

        if not items_of_slot:
            return None

        elif len(items_of_slot) == 1:
            return items_of_slot[0]

        else:
            return items_of_slot