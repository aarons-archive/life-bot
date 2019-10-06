
class Account:

    def __init__(self, data, inventory):
        self.id = data.get("id", "N/A")
        self.background = data.get("background", "N/A")
        self.cash = data.get("cash", "N/A")
        self.bank = data.get("bank", "N/A")
        self.inventory = inventory

    def __repr__(self):
        return "<{0.__module__}.Account id={0.id}>".format(self)

    def __str__(self):
        return self.id



