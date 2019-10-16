
class SubmachineGun:

    def __init__(self, item):
        self.id = 101
        self.name = "Sub Machine Gun"
        self.power = 1
        self.damage = 5
        self.ammo = 5
        self.magazine = 50

        self.owner = item["owner"]

    def __repr__(self):
        return "<Item id={0.id} name={0.name} power={0.power} owner={0.owner}>".format(self)
