
class BasePower:

    def __init__(self):
        self.count = 0
        self.stackable = False
        self.base_type = "PowerWeapon"

    def __repr__(self):
        return "<{0.__class__.__name__} id={0.id} base_name={0.base_name!r} name={0.name!r} power={0.power} owner={0.owner} count={0.count} slot={0.slot!r} stackable={0.stackable} base_type={0.base_type!r} sub_type={0.sub_type!r}>".format(self)


class Bazooka(BasePower):

    def __init__(self, item):
        super().__init__()

        self.id = 201

        self.sub_type = "RockerLauncher"

        self.base_name = "Bazooka"
        self.name = item["name"]

        self.power = item["power"]
        self.owner = item["owner"]
        self.count = item["count"]
        self.slot = item["slot"]
