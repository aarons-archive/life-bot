
class BasePower:

    def __init__(self):
        self.count = 0
        self.stackable = False
        self.type = "PowerWeapon"

    def __repr__(self):
        return "<{0.__class__.__name__} id={0.id} base_name={0.base_name!r} name={0.name!r} power={0.power} owner={0.owner} count={0.count} stackable={0.stackable} type={0.type!r}>".format(self)


class RocketLauncher(BasePower):

    def __init__(self, item):
        super().__init__()

        self.id = 201

        self.base_name = "Rocket Launcher"
        self.name = item["name"]

        self.power = item["power"]
        self.owner = item["owner"]
        self.count = item["count"]
