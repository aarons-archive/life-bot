
class BaseSecondary:

    def __init__(self):
        self.count = 0
        self.stackable = False
        self.type = "SecondaryWeapon"

    def __repr__(self):
        return "<{0.__class__.__name__} id={0.id} base_name={0.base_name!r} name={0.name!r} power={0.power} owner={0.owner} count={0.count} stackable={0.stackable} type={0.type!r}>".format(self)


class SubMachineGun(BaseSecondary):

    def __init__(self, item):
        super().__init__()

        self.id = 201

        self.base_name = "Sub Machine Gun"
        self.name = item["name"]

        self.power = item["power"]
        self.owner = item["owner"]
        self.count = item["count"]
