from enum import Enum
from backend.errors import InventoryError, OrderError

class IngredientType(Enum):
    BURGERBUN = 1
    WRAP = 2
    FILLING = 3
    PATTY = 4
    SIDE = 5
    DRINK = 6

class Ingredient:
    def __init__(self, name, price, quantity, iType, servingSizes, unit="unit"):
        self._name = name.lower()
        self._price = price
        self._quantity = quantity
        self._iType = iType
        self._servingSizes = servingSizes
        self._unit = unit

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def iType(self):
        return self._iType

    @property
    def quantity(self):
        return self._quantity      

    @property
    def servingSizes(self):
        return self._servingSizes
    
    @property
    def unit(self):
        return self._unit

    def decreaseStock(self, size, quantity):
        if size == "regular":
            q = quantity
        else:
            q = quantity * self._servingSizes[size]
        if(q > self._quantity):
            raise InventoryError("Insufficient stock for " + self._name.lower())
        self._quantity -= q    

    def addStock(self, quantity, size="regular"):
        if size == "regular":
            q = quantity
        else:
            q = quantity * self._servingSizes[size]
        self._quantity += q

class Inventory:
    def __init__(self):
        self._ingredients = []

    def getIngredient(self, name):
        for ingredient in self._ingredients:
            if ingredient.name.lower() == name.lower():
                return ingredient
        raise InventoryError(name.capitalize() + " does not exist")

    def addIngredient(self, name, price, quantity, iType, servingSizes, unit="unit"):
        allowedUnits = ["g", "ml", "unit"]
        try:
            q = int(quantity)
        except ValueError:
            raise InventoryError("Please enter integer quantity")
        else:
            if q < 0:
                raise InventoryError("Please enter positive quantity for " + name.lower())
        try:
            p = float(price)
        except ValueError:
            raise InventoryError("Please enter valid price for" + name.lower())
        else:
            if p <= 0:
                raise InventoryError("Please enter valid price for " + name.lower())

        if unit not in allowedUnits:
            raise InventoryError("Please enter valid unit")
        if unit == "ml" and iType != IngredientType.DRINK:
            raise InventoryError(name.capitalize() + " must be type drink to be stored in ml")
        regularTypes = [IngredientType.BURGERBUN, IngredientType.WRAP, 
                        IngredientType.FILLING, IngredientType.PATTY]

        if iType in regularTypes and unit != "unit":
            raise InventoryError(iType.name.capitalize() + " must be stored as unit")

        for ingredient in self._ingredients:
            if ingredient.name.lower() == name.lower():
                raise InventoryError(name.lower() + " already exists")
        ingredient = Ingredient(name, price, quantity, iType, servingSizes, unit)
        self._ingredients.append(ingredient)

    def updateStockSide(self, name, quantity, servingSize="regular"):
        ingredient = self.getIngredient(name)
        if servingSize not in ingredient.servingSizes:
            raise InventoryError("Incorrect serving size for " + name.lower())
        return ingredient.decreaseStock(servingSize, quantity)

    def updateStockMain(self, ingredients):
        for name, quantity in ingredients.items():
            if self.checkSufficientStock(name, quantity) == False:
                raise InventoryError("Insufficient stock for " + name.lower())
        for name, quantity in ingredients.items():
            ingredient = self.getIngredient(name)
            ingredient.decreaseStock("regular", quantity)

    def checkSufficientStock(self, name, quantity, servingSize='regular'):
        ingredient = self.getIngredient(name)
        if ingredient.quantity >= quantity*ingredient.servingSizes[servingSize]:
            return True
        return False 

    @property
    def ingredients(self):
        return self._ingredients

    def isBurgerValid(self, ingredients):
        # check burger order is valid
        self.checkNegativeQuantity(ingredients)
        self.checkOnlyBurgerOrWrap(ingredients)
        self.checkBunNumber(ingredients)

    def isWrapValid(self, ingredients):
        # check wrap order is valid
        self.checkNegativeQuantity(ingredients)
        self.checkOnlyBurgerOrWrap(ingredients)
        self.checkOnlyOneWrap(ingredients)

    def checkOnlyBurgerOrWrap(self, ingredients):
        buns = 0
        wraps = 0
        for name, quantity in ingredients.items():
            ingredient = self.getIngredient(name)
            if ingredient.iType == IngredientType.BURGERBUN:
                buns += quantity
            elif ingredient.iType == IngredientType.WRAP:
                wraps += quantity
            
            if buns > 0 and wraps > 0:
                raise OrderError("Cannot choose both burger and wrap")

    def checkOnlyOneWrap(self, ingredients):
        wraps = 0
        for name, quantity in ingredients.items():
            ingredient = self.getIngredient(name)
            if ingredient.iType == IngredientType.WRAP:
                wraps += quantity
        if wraps != 1:
            raise OrderError("Must select one wrap bread")

    def checkBunNumber(self, ingredients):
        buns = 0
        patties = 0
        for name, quantity in ingredients.items():
            ingredient = self.getIngredient(name)
            if ingredient.iType == IngredientType.BURGERBUN:
                buns += quantity
            elif ingredient.iType == IngredientType.PATTY:
                patties += quantity
        if patties <= 0:
            maximumBuns = 2
        else:
            maximumBuns = patties + 1
        if buns < 2 or buns > maximumBuns:
            print(buns, maximumBuns)
            msg = "Number of buns must be between 2 and " + str(maximumBuns)
            raise OrderError(msg)

    def checkNegativeQuantity(self, ingredients):
        for name, quantity in ingredients.items():
            ingredient = self.getIngredient(name)
            if quantity < 0:
                raise OrderError("Cannot enter negative quantity")

    def updateInventory(self, ingredients):
        for name, quantity in ingredients.items():
            ingredient = self.getIngredient(name)
            if quantity > 0:
                ingredient.addStock(quantity)
            elif quantity < 0:
                ingredient.decreaseStock("regular", abs(quantity))
