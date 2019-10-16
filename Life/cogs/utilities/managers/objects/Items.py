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
