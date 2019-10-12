
class Account:

    def __init__(self, data, inventory):
        self.id = data.get("id", "N/A")
        self.cash = data.get("cash", "N/A")
        self.bank = data.get("bank", "N/A")
        self.inventory = inventory

    def __repr__(self):
        return "<Account id={0.id} cash={0.cash} bank={0.bank}>".format(self)

    def __str__(self):
        return self.id





