from backend.inventory import Inventory, Ingredient

class Main:
    def __init__(self, ingredients):
        self._ingredients = ingredients

    @property
    def ingredients(self):
        return self._ingredients

    def calculateCost(self, inventory):
        cost = 0
        for name, quantity in self._ingredients.items():
            if quantity > 0:
                ingredient = inventory.getIngredient(name)
                cost += ingredient.price * quantity
        return cost

    def __str__(self):
        parts = []
        parts.append("Main Order: Ingredients List")
        for name, quantity in self._ingredients.items():
            if quantity > 0:
                parts.append("{} Qty: {}".format(name, quantity))
        return "\n".join(parts)

