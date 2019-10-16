
class Pistol:

    def __init__(self, item):
        self.id = 1
        self.name = "Pistol"
        self.power = 1
        self.damage = 5
        self.ammo = 10
        self.magazine = 20

        self.owner = item["owner"]


