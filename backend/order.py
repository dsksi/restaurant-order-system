from backend.inventory import Inventory, Ingredient, IngredientType
from backend.errors import OrderError
from backend.main import Main
from backend.side import SideDrink

class Order:
    def __init__(self, ID):
        self._ID = ID
        self._prepared = False
        self._paid = False
        self._mains = []
        self._sidesAndDrinks = []

    @property
    def ID(self):
        return self._ID

    def displayOrderID(self):
        return "Your Order ID is {}".format(self._ID)

    @property
    def paid(self):
        return self._paid

    @property
    def prepared(self):
        return self._prepared

    def updatePrepared(self):
        self._prepared = True

    @property
    def mainOrders(self):
        return self._mains

    @property
    def sidesAndDrinks(self):
        return self._sidesAndDrinks

    def cancel(self, inventory):
        for main in self._mains:
            for name, quantity in main.ingredients.items():
                ingredient = inventory.getIngredient(name)
                ingredient.addStock(quantity)
        for side in self._sidesAndDrinks:
            ingredient = inventory.getIngredient(side.name)
            ingredient.addStock(side.quantity, side.servingSize)
        return "Order cancelled" 
    
    def addBurgerMain(self, inventory, ingredients):
        if self.paid == True:
            raise OrderError("Order is already complete, please start new order.")
        # check burger order is valid
        inventory.isBurgerValid(ingredients)
        inventory.updateStockMain(ingredients)
        self._mains.append(Main(ingredients))
        return "Main added to order"

    def addStandardBurger(self, inventory):
        ingredients = {"sesame bun":2,"beef":1,"tomato":1, "cheddar cheese":1}
        msg = self.addBurgerMain(inventory, ingredients)
        return msg

    def addWrapMain(self, inventory, ingredients):
        if self.paid == True:
            raise OrderError("Order is already complete, please start new order.")
        # check wrap order is valid
        inventory.isWrapValid(ingredients)
        inventory.updateStockMain(ingredients)
        self._mains.append(Main(ingredients))
        return "Main added to order"

    def addStandardWrap(self, inventory):
        ingredients = {"flatbread":1, "chicken":1, "lettuce":1, "cheddar cheese":1}
        msg = self.addWrapMain(inventory, ingredients)
        return msg

    def addSide(self, inventory, name, quantity, size):
        if self.paid == True:
            raise OrderError("Order is already complete, please start new order.")
        if quantity < 0:
                raise OrderError("Cannot enter negative quantity")
        inventory.updateStockSide(name, quantity, size)
        self._sidesAndDrinks.append(SideDrink(name, quantity, size))  
        return "Sides added to order"

    def addDrink(self, inventory, name, quantity, size):
        if self.paid == True:
            raise OrderError("Order is already complete, please start new order.")
        if quantity < 0:
                raise OrderError("Cannot enter negative quantity")
        inventory.updateStockSide(name, quantity, size)
        self._sidesAndDrinks.append(SideDrink(name, quantity, size))  
        return "Drinks added to order"

    def calculateTotalPrice(self, inventory):
        cost = 0
        for main in self._mains:
            cost += main.calculateCost(inventory)
        for side in self._sidesAndDrinks:
            cost += side.calculateCost(inventory)
        return cost        

    def submitAndPay(self, payStatus):
        #customer will be lead to external payment system
        #payment system will return boolean value to indicate successful
        #or unsuccessful payment
        if len(self.mainOrders) == 0 and len(self.sidesAndDrinks) == 0:
            raise OrderError("Must order before checkout")
        if payStatus == True:
            self._paid = True
        else:
            raise OrderError("Payment unsuccessful")

    def displayOrder(self, inventory):
        parts = []
        parts.append("====================================")
        parts.append("Order ID {}".format(self._ID))
        parts.append("Order status:")
        if self._paid == False:
            parts.append("- Pending: unpaid")
        else:
            if self._prepared == False:
                parts.append("- Active: in service")
            else:
                parts.append("- Finished: order prepared")
        cost = self.calculateTotalPrice(inventory)
        for main in self._mains:
            parts.append("Main order")
            parts.append(main.__str__())
        for sideDrink in self._sidesAndDrinks:
            parts.append("Side order")
            parts.append(sideDrink.__str__())
        parts.append("Total Fee: ${}".format(cost))
        parts.append("====================================")
        return "\n".join(parts)
