
class BaseChestplate:

    def __init__(self):
        self.count = 0
        self.stackable = False
        self.base_type = "chestplate"

    def __repr__(self):
        return "<{0.__class__.__name__} id={0.id} owner={0.owner} power={0.power} count={0.count} stackable={0.stackable} slot={0.slot!r} base_name={0.base_name!r} name={0.name!r} base_type={0.base_type!r} type={0.type!r}>".format(self)


class StarterChestplate(BaseChestplate):

    def __init__(self, item):
        super().__init__()

        self.id = 101

        self.type = "starter"

        self.base_name = "Starter Chestplate"
        self.name = item.get("name")

        self.power = item.get("power")
        self.owner = item.get("owner")
        self.count = item.get("count")
        self.slot = item.get("slot")

