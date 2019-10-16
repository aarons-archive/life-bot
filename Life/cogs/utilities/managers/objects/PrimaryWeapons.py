
class Pistol:

    def __init__(self, item):
        self.id = 1
        self.name = "Pistol"
        self.power = 1
        self.damage = 5
        self.ammo = 10
        self.magazine = 20

        self.owner = item["owner"]

    def __repr__(self):
        return "<Item id={0.id} name={0.name} power={0.power} owner={0.owner}>".format(self)


