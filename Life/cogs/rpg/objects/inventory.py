from .boots import *
from .chestplate import *
from .helmet import *

item_ids = {
    1: StarterBoots,
    101: StarterChestplate,
    201: StarterHelmet
}


class Inventory:

    def __init__(self, raw_inventory: list):

        self.raw_items = raw_inventory
        self.items = self.get_inventory_objects(self.raw_items)

    @staticmethod
    def get_inventory_objects(items: list):

        inventory = []

        for item in items:
            item_object = item_ids.get(item["id"], None)
            if not item_object:
                continue
            inventory.append(item_object(item))

        return inventory

    @staticmethod
    def get_item_id(item_list: list, item_id: int):

        items_of_id = [item for item in item_list if item.id == item_id]

        if not items_of_id:
            return None

        return items_of_id

    @staticmethod
    def get_item_slot(item_list: list, item_slot: str):

        items_of_slot = [item for item in item_list if item.slot == item_slot]

        if not items_of_slot:
            return None

        return items_of_slot

    @staticmethod
    def get_item_base_name(item_list: list, item_base_name: str):

        items_of_base_name = [item for item in item_list if item.base_name == item_base_name]

        if not items_of_base_name:
            return None

        return items_of_base_name

    @staticmethod
    def get_item_name(item_list: list, item_name: str):

        items_of_name = [item for item in item_list if item.name == item_name]

        if not items_of_name:
            return None

        return items_of_name

    @staticmethod
    def get_item_base_type(item_list: list, item_base_type: str):

        items_of_base_type = [item for item in item_list if item.base_type == item_base_type]

        if not items_of_base_type:
            return None

        return items_of_base_type

    @staticmethod
    def get_item_type(item_list: list, item_type: str):

        items_of_type = [item for item in item_list if item.type == item_type]

        if not items_of_type:
            return None

        return items_of_type

