from backend.inventory import Inventory

class SideDrink:
    def __init__(self, name, quantity, size="Regular"):
        self._name = name
        self._quantity = quantity
        self._size = size

    @property
    def name(self):
        return self._name

    @property
    def servingSize(self):
        return self._size

    @property
    def quantity(self):
        return self._quantity

    def calculateCost(self, inventory):
        if self.quantity > 0:
            ingredient = inventory.getIngredient(self.name)
            cost = ingredient.price * self.quantity * ingredient.servingSizes[self.servingSize]
            return cost
        else:
            return 0
            
    def __str__(self):
        if self.quantity > 0:
            return "{}, Qty: {}, Size: {}".format(self._name, self._quantity, self._size)
        else:
            return ""
            
