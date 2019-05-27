from backend.system import RestaurantSystem
from backend.inventory import IngredientType

def bootstrap_system():
    sys = RestaurantSystem()
    inv = sys.inventory
    regularSize = {"regular" : 1}
    nuggetSize = {"small":3,"medium":6, "large": 9}
    friesSize = {"small":100,"medium":150, "large": 200}
    drinkSize = {"small": 250, "medium":450, "large": 600}
    sundaeSize = {"small":100, "medium":150, "large": 200}

    for name in ["tomato", "cheddar cheese", "lettuce", "swiss cheese", "tomato sauce"]:
        inv.addIngredient(name, 1, 100, IngredientType.FILLING, regularSize)
    for name in ["sesame bun", "muffin bun"]:
        inv.addIngredient(name, 1, 100, IngredientType.BURGERBUN, regularSize)
    for name in ["chicken", "beef"]:
        inv.addIngredient(name, 4, 100, IngredientType.PATTY, regularSize)
    for name in ["flatbread", "wholewheat"]:
        inv.addIngredient(name, 1, 100, IngredientType.WRAP, regularSize)
    for name in ["can coke", "can fanta", "can sprite"]:
        inv.addIngredient(name, 3, 100, IngredientType.DRINK, regularSize)
    for name in ["bottle coke", "bottle fanta", "bottle sprite"]:
        inv.addIngredient(name, 5, 100, IngredientType.DRINK, regularSize)
    for name in ["chocolate sundae", "strawberry sundae"]:
        inv.addIngredient(name, 0.02, 10000, IngredientType.SIDE, sundaeSize, "g")
    inv.addIngredient("orange juice", 0.01, 10000, IngredientType.DRINK, drinkSize, "ml")
    inv.addIngredient("chicken nugget", 1, 1000, IngredientType.SIDE, nuggetSize)
    inv.addIngredient("fries", 0.01, 1000, IngredientType.SIDE, friesSize, "g")
    
    #test order
    order = sys.createOrder()
    order.addStandardBurger(sys.inventory)
    order.addSide(sys.inventory, "fries", 1, "medium")
    order.addSide(sys.inventory, "strawberry sundae", 2, "large")
    sys.checkout(1)
    order = sys.createOrder()
    order.addStandardBurger(sys.inventory)
    order.addStandardBurger(sys.inventory)
    order.addSide(sys.inventory, "chocolate sundae", 2, "large")
    order = sys.createOrder()
    ingredients = {"tomato":1, "cheddar cheese":1,"beef":1, "sesame bun":2}
    order.addBurgerMain(sys.inventory, ingredients)
    order.addSide(sys.inventory, "chicken nugget", 2, "small")
    sys.checkout(2)
    sys.checkout(3)
    return sys

