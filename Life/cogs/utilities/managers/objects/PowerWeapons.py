
class RocketLauncher:

    def __init__(self, item):
        self.id = 201
        self.name = "Rocket launcher"
        self.power = 1
        self.damage = 2
        self.ammo = 3
        self.magazine = 9

        self.owner = item["owner"]
