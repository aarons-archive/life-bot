
class BasePower:

    def __init__(self):
        self.count = 0
        self.stackable = False

    def __repr__(self):
        return "<Item id={0.id} name={0.name!r} power={0.power} owner={0.owner}>".format(self)


class RocketLauncher(BasePower):

    def __init__(self, item):
        super().__init__()

        self.id = 201
        self.name = "Rocket launcher"
        self.owner = item["owner"]

        self.power = 5
