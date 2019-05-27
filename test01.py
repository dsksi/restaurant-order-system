from backend.system import RestaurantSystem
from backend.errors import OrderError, InventoryError
from backend.order import Order
from backend.main import Main
from backend.side import SideDrink
from backend.inventory import Inventory, Ingredient, IngredientType

import pytest

@pytest.fixture()
def system_fixture():
    sys = RestaurantSystem()
    inv = sys.inventory
    regularSize = {"regular" : 1}
    nuggetSize = {"small":3,"medium":6, "large": 9}
    drinkSize = {"small": 250, "medium":450, "large": 600}
    sundaeSize = {'small': 100, "medium": 150, 'large': 200}

    for name in ["tomato", "cheddar cheese", "lettuce", "swiss cheese"]:
        inv.addIngredient(name, 1, 100, IngredientType.FILLING, regularSize)
    for name in ["sesame bun", "muffin bun"]:
        inv.addIngredient(name, 1, 100, IngredientType.BURGERBUN, regularSize)
    for name in ["chicken", "beef"]:
        inv.addIngredient(name, 5, 100, IngredientType.PATTY, regularSize)
    for name in ["flatBread", "wholeWheat"]:
        inv.addIngredient(name, 1, 100, IngredientType.WRAP, regularSize)
    for name in ["Can Coke", "Can Fanta", "Can Sprite"]:
        inv.addIngredient(name, 5, 100, IngredientType.DRINK, regularSize)
    for name in ["Bottle Coke", "Bottle Fanta", "Bottle Sprite"]:
        inv.addIngredient(name, 5, 100, IngredientType.DRINK, regularSize)
    for name in ["chocolate sundae", "strawberry sundae"]:
        inv.addIngredient(name, 0.04, 10000, IngredientType.SIDE, sundaeSize)
    inv.addIngredient("Orange Juice", 0.02, 10000, IngredientType.DRINK, drinkSize, "ml")
    inv.addIngredient("Chicken Nugget", 1, 1000, IngredientType.SIDE, nuggetSize, "g")
    return sys

'''
test01: Create and add items to online order - US1.1, 1.2, 1.3, 1.8
'''
### User Story 1.1 - Make a customised main order ###
# test initial order creation in RestuarantSystem
def test_create_order(system_fixture):
    assert system_fixture.pendingOrders == []
    system_fixture.createOrder()
    assert system_fixture.finishedOrders == []
    assert system_fixture.activeOrders == []
    assert len(system_fixture.pendingOrders) == 1
    assert system_fixture.pendingOrders[0].ID == 1
    assert system_fixture.orderIDCounter == 2

def test_create_multiple_orders(system_fixture):
    for i in range(5):
        order = system_fixture.createOrder()
        assert len(system_fixture.pendingOrders) == (i+1)
        assert order.ID == (i+1)

# tests for adding main orders and sides/drinks to order
# tests validity of main order/sides/drinks
def test_successful_add_burger_main(system_fixture):
    order = system_fixture.createOrder()
    #check order initialised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":100, "cheddar cheese":1,"beef":1,"sesame bun":2}
    msg = order.addBurgerMain(system_fixture.inventory, ingredients)
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0
    for name, quantity in ingredients.items():
        assert order.mainOrders[0].ingredients[name] == quantity
    assert order.calculateTotalPrice(system_fixture.inventory) == 108    
    for name, quantity in ingredients.items():
        ingredient = system_fixture.inventory.getIngredient(name)
        assert ingredient.quantity == (100 - quantity)
    assert msg == "Main added to order"

def test_successful_add_multiple_burger_main(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    cost = 0
    ingredients1 = {"tomato":1, "cheddar cheese":1, "beef":1, "sesame bun":2}
    ingredients2 = {"tomato":1, "cheddar cheese":1,"beef":2,"sesame bun":3}
    ingredients3 = {"tomato":1, "cheddar cheese":1,"beef":3,"sesame bun":4}
    ingredients4 = {"tomato":1, "cheddar cheese":1,"beef":4,"sesame bun":5}
    ingredients = [ingredients1, ingredients2, ingredients3, ingredients4] 
    qtyUsed = {"tomato":0, "cheddar cheese":0, "beef":0, "sesame bun":0}    
    for i in range(len(ingredients)):
        msg = order.addBurgerMain(system_fixture.inventory, ingredients[i])
        assert len(order.mainOrders) == (i+1)
        assert len(order.sidesAndDrinks) == 0
        for name, quantity in ingredients[i].items():
            assert order.mainOrders[i].ingredients[name] == quantity
        cost += order.mainOrders[i].calculateCost(system_fixture.inventory)
        assert order.calculateTotalPrice(system_fixture.inventory) == cost 
        for name, quantity in ingredients[i].items():
            qtyUsed[name] += quantity
            ingredient = system_fixture.inventory.getIngredient(name)
            assert ingredient.quantity == (100 - qtyUsed[name])
        assert msg == "Main added to order"

def test_fail_burger_main_no_buns_selected(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":1}
    for i in range(1,5):
        try:
            ingredients["beef"] = i
            order.addBurgerMain(system_fixture.inventory, ingredients)
        except OrderError as oe:
            maxBuns = i + 1
            msg = "Number of buns must be between 2 and " + str(maxBuns)
            assert oe.msg == msg
        else:
            assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_burger_main_double_burger_more_buns(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":2,"sesame bun":4}
    try:
        order.addBurgerMain(system_fixture.inventory, ingredients)
    except OrderError as oe:
        assert oe.msg == "Number of buns must be between 2 and 3"
    else:
        assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_burger_main_more_buns_selected(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":1,"sesame bun":3}
    for i in range(3, 8):
        try:
            ingredients["beef"] = i - 2
            ingredients["sesame bun"] = i 
            order.addBurgerMain(system_fixture.inventory, ingredients)
        except OrderError as oe:
            maxBuns = i - 1
            msg = "Number of buns must be between 2 and " + str(maxBuns)
            assert oe.msg == msg
        else:
            assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_burger_main_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":101,"sesame bun":2}
    try:
        order.addBurgerMain(system_fixture.inventory, ingredients)
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for beef"
    else:
        assert False
    assert len(order.mainOrders) == 0

def test_success_burger_main_no_patty(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"sesame bun":2}
    assert "Main added to order" == order.addBurgerMain(system_fixture.inventory, ingredients)
    assert len(order.mainOrders) == 1

def test_fail_burger_main_no_patty_one_bun(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1}
    try:
        order.addBurgerMain(system_fixture.inventory, ingredients)
    except OrderError as oe:
        msg = "Number of buns must be between 2 and 2"
        assert oe.msg == msg
    else:
        assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_burger_main_negative_quantity(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":-1, "cheddar cheese":1}
    try:
        order.addBurgerMain(system_fixture.inventory, ingredients)
    except OrderError as oe:
        msg = "Cannot enter negative quantity"
        assert oe.msg == msg
    else:
        assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_burger_already_paid(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    order.addBurgerMain(system_fixture.inventory, {"sesame bun":2, "beef":1, "tomato":1, "cheddar cheese":1})
    order.submitAndPay(True)
    assert order.paid == True
    assert len(order.mainOrders) == 1
    try:
        order.addBurgerMain(system_fixture.inventory, {"sesame bun":2, "beef":1, "tomato":1, "cheddar cheese":1})
    except OrderError as oe:
        assert oe.msg == "Order is already complete, please start new order."
    else:
        assert False
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

def test_successful_add_wrap_main(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":100, "cheddar cheese":1,"chicken":1,"flatbread":1}
    msg = order.addWrapMain(system_fixture.inventory, ingredients)
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0 
    for name, quantity in ingredients.items():
        assert order.mainOrders[0].ingredients[name] == quantity
    assert order.calculateTotalPrice(system_fixture.inventory) == 107
    for name, quantity in ingredients.items():
        ingredient = system_fixture.inventory.getIngredient(name)
        assert ingredient.quantity == (100 - quantity)
    assert msg == "Main added to order"

def test_successful_add_multiple_wrap_main(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    cost = 0
    ingredients1 = {"tomato":1, "cheddar cheese":1, "beef":1, "flatbread":1}
    ingredients2 = {"tomato":1, "cheddar cheese":1,"beef":2,"flatbread":1}
    ingredients3 = {"tomato":1, "cheddar cheese":1,"beef":3,"flatbread":1}
    ingredients4 = {"tomato":1, "cheddar cheese":1,"beef":4,"flatbread":1}
    ingredients = [ingredients1, ingredients2, ingredients3, ingredients4] 
    qtyUsed = {"tomato":0, "cheddar cheese":0, "beef":0, "flatbread":0}    
    for i in range(len(ingredients)):
        msg = order.addWrapMain(system_fixture.inventory, ingredients[i])
        assert msg == "Main added to order"
        assert len(order.mainOrders) == (i+1)
        assert len(order.sidesAndDrinks) == 0
        for name, quantity in ingredients[i].items():
            assert order.mainOrders[i].ingredients[name] == quantity
        cost += order.mainOrders[i].calculateCost(system_fixture.inventory)
        assert order.calculateTotalPrice(system_fixture.inventory) == cost 
        for name, quantity in ingredients[i].items():
            qtyUsed[name] += quantity
            ingredient = system_fixture.inventory.getIngredient(name)
            assert ingredient.quantity == (100 - qtyUsed[name])

def test_fail_no_wraps_seleted(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"chicken":1}
    try:
        order.addWrapMain(system_fixture.inventory, ingredients)
    except OrderError as oe:
        assert oe.msg == "Must select one wrap bread"
    else:
        assert(False)
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_more_wraps_selected(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"chicken":1,"flatbread":2}
    for i in range(2, 5):
        ingredients["flatbread"] = i
        try:
            order.addWrapMain(system_fixture.inventory, ingredients)
        except OrderError as oe:
            assert oe.msg == "Must select one wrap bread"
        else:
            assert False
        assert len(order.mainOrders) == 0
        assert len(order.sidesAndDrinks) == 0

def test_fail_wrap_main_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":101,"flatbread":1}
    try:
        order.addWrapMain(system_fixture.inventory, ingredients)
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for beef"
    else:
        assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_wrap_main_negative_quantity(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":-1, "cheddar cheese":1}
    try:
        order.addWrapMain(system_fixture.inventory, ingredients)
    except OrderError as oe:
        msg = "Cannot enter negative quantity"
        assert oe.msg == msg
    else:
        assert False
    assert len(order.mainOrders) == 0

def test_fail_wrap_already_paid(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    order.addStandardBurger(system_fixture.inventory)
    order.submitAndPay(True)
    assert order.paid == True
    assert len(order.mainOrders) == 1
    try:
        order.addWrapMain(system_fixture.inventory, {"flatbread":1, "beef":1, "tomato":1, "cheddar cheese":1})
    except OrderError as oe:
        assert oe.msg == "Order is already complete, please start new order."
    else:
        assert False
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

### User Story 1.2 - Order sides ###
def test_success_add_side_chicken_nuggets(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    msg = order.addSide(system_fixture.inventory, "chicken nugget", 2, "small")
    assert msg == "Sides added to order"
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 1
    ingredient = system_fixture.inventory.getIngredient("chicken nugget")
    assert ingredient.quantity == (1000 - 6)
    assert order.calculateTotalPrice(system_fixture.inventory) == 6
    system_fixture.inventory.updateInventory({"chicken nugget": -(1000 - 6 - 3)})
    assert ingredient.quantity == 3
    msg = order.addSide(system_fixture.inventory, "chicken nugget", 1, "small")
    assert msg == "Sides added to order"
    assert len(order.sidesAndDrinks) == 2
    assert order.calculateTotalPrice(system_fixture.inventory) == 9
    assert ingredient.quantity == 0

def test_fail_add_side_chicken_nugget_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addSide(system_fixture.inventory, "chicken nugget", 10000, "large") 
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for chicken nugget"
    assert len(order.sidesAndDrinks) == 0
    ingredient = system_fixture.inventory.getIngredient("chicken nugget")
    assert ingredient.quantity == 1000
    assert order.calculateTotalPrice(system_fixture.inventory) == 0

def test_fail_add_side_chicken_nugget_negative_quantity(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addSide(system_fixture.inventory, "chicken nugget", -10000, "large") 
    except OrderError as oe:
        assert oe.msg == "Cannot enter negative quantity"
    assert len(order.sidesAndDrinks) == 0
    ingredient = system_fixture.inventory.getIngredient("chicken nugget")
    assert ingredient.quantity == 1000
    assert order.calculateTotalPrice(system_fixture.inventory) == 0

def test_fail_add_side_already_paid(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    order.addStandardBurger(system_fixture.inventory)
    order.submitAndPay(True)
    assert order.paid == True
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addSide(system_fixture.inventory, "chicken nuggets", 1, "small")
    except OrderError as oe:
        assert oe.msg == "Order is already complete, please start new order."
    else:
        assert False
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

def test_success_add_sundae(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    msg = order.addSide(system_fixture.inventory, "chocolate sundae", 2, "small")
    assert msg == "Sides added to order"
    assert len(order.sidesAndDrinks) == 1
    assert len(order.mainOrders) == 0
    ingredient = system_fixture.inventory.getIngredient("chocolate sundae")
    assert ingredient.quantity == (10000 - 200)
    assert order.calculateTotalPrice(system_fixture.inventory) == 8

def test_fail_add_sundae_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addSide(system_fixture.inventory, "chocolate sundae", 10000, "large") 
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for chocolate sundae"
    assert len(order.sidesAndDrinks) == 0
    assert len(order.mainOrders) == 0
    ingredient = system_fixture.inventory.getIngredient("chocolate sundae")
    assert ingredient.quantity == 10000
    assert order.calculateTotalPrice(system_fixture.inventory) == 0

def test_fail_add_sundae_negative_quantity(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addSide(system_fixture.inventory, "chocolate sundae", -10000, "large") 
    except OrderError as oe:
        assert oe.msg == "Cannot enter negative quantity"
    assert len(order.sidesAndDrinks) == 0
    assert len(order.mainOrders) == 0
    ingredient = system_fixture.inventory.getIngredient("chocolate sundae")
    assert ingredient.quantity == 10000
    assert order.calculateTotalPrice(system_fixture.inventory) == 0

### User Story 1.3 - Order Drinks ###
def test_success_add_drink_orange_juice(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    msg = order.addDrink(system_fixture.inventory, "orange juice", 2, "small")
    assert msg == "Drinks added to order"
    assert len(order.sidesAndDrinks) == 1
    assert len(order.mainOrders) == 0
    ingredient = system_fixture.inventory.getIngredient("orange juice")
    assert ingredient.quantity == (10000 - 2 * 250)
    assert order.calculateTotalPrice(system_fixture.inventory) == 0.02*2*250
    system_fixture.inventory.updateInventory({"orange juice": -(10000-750)})
    msg = order.addDrink(system_fixture.inventory, "orange juice", 1, "small")
    assert msg == "Drinks added to order"
    assert ingredient.quantity == 0

def test_fail_add_drink_orange_juice_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addDrink(system_fixture.inventory, "orange juice", 10000, "large") 
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for orange juice"
    assert len(order.sidesAndDrinks) == 0
    assert len(order.mainOrders) == 0
    ingredient = system_fixture.inventory.getIngredient("orange juice")
    assert ingredient.quantity == 10000
    assert order.calculateTotalPrice(system_fixture.inventory) == 0

def test_fail_add_drink_orange_juice_negative_quantity(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addDrink(system_fixture.inventory, "orange juice", -10000, "large") 
    except OrderError as oe:
        assert oe.msg == "Cannot enter negative quantity"
    assert len(order.sidesAndDrinks) == 0
    assert len(order.mainOrders) == 0
    ingredient = system_fixture.inventory.getIngredient("orange juice")
    assert ingredient.quantity == 10000
    assert order.calculateTotalPrice(system_fixture.inventory) == 0

def test_fail_add_drink_already_paid(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    order.addStandardBurger(system_fixture.inventory)
    order.submitAndPay(True)
    assert order.paid == True
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0
    try:
        order.addDrink(system_fixture.inventory, "Can Coke", 1, "regular")
    except OrderError as oe:
        assert oe.msg == "Order is already complete, please start new order."
    else:
        assert False
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

### User Story 1.8 - Order standard main ###
def test_success_add_standard_burger(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    assert "Main added to order" == order.addStandardBurger(system_fixture.inventory)
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0
    assert order.calculateTotalPrice(system_fixture.inventory) == 9
    ingredients = {"sesame bun":2, "beef":1, "tomato":1, "cheddar cheese":1}
    for name, quantity in ingredients.items():
        ingredient = system_fixture.inventory.getIngredient(name)
        assert ingredient.quantity == (100 - quantity)

def test_fail_addStandardBurger_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    assert system_fixture.inventory.getIngredient("sesame bun").quantity == 100
    assert system_fixture.inventory.getIngredient("tomato").quantity == 100
    system_fixture.inventory.updateInventory({"sesame bun": -99})
    assert system_fixture.inventory.getIngredient("sesame bun").quantity == 1
    assert system_fixture.inventory.getIngredient("tomato").quantity == 100
    try:
        order.addStandardBurger(system_fixture.inventory)
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for sesame bun"
    else:
        assert False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

def test_fail_standard_burger_already_paid(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    order.addStandardBurger(system_fixture.inventory)
    order.submitAndPay(True)
    assert order.paid == True
    assert len(order.mainOrders) == 1
    try:
        order.addStandardBurger(system_fixture.inventory)
    except OrderError as oe:
        assert oe.msg == "Order is already complete, please start new order."
    else:
        assert False
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

def test_success_addStandardWrap(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    msg = order.addStandardWrap(system_fixture.inventory)
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0
    assert order.calculateTotalPrice(system_fixture.inventory) == 8
    assert msg == "Main added to order"
    ingredients = {"flatbread":1, "chicken":1, "lettuce":1, "cheddar cheese":1}
    for name, quantity in ingredients.items():
        ingredient = system_fixture.inventory.getIngredient(name)
        assert ingredient.quantity == (100 - quantity)

def test_fail_addStandardWrap_insufficient_stock(system_fixture):
    order = system_fixture.createOrder()
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    assert system_fixture.inventory.getIngredient("chicken").quantity == 100
    assert system_fixture.inventory.getIngredient("lettuce").quantity == 100
    system_fixture.inventory.updateInventory({"chicken": -100})
    assert system_fixture.inventory.getIngredient("chicken").quantity == 0
    assert system_fixture.inventory.getIngredient("lettuce").quantity == 100
    try:
        order.addStandardWrap(system_fixture.inventory)
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for chicken"
    else:
        assert False
    assert len(order.mainOrders) == 0

def test_fail_standard_wrap_already_paid(system_fixture):
    order = system_fixture.createOrder()
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0
    order.addStandardBurger(system_fixture.inventory)
    order.submitAndPay(True)
    assert order.paid == True
    assert len(order.mainOrders) == 1
    try:
        order.addStandardWrap(system_fixture.inventory)
    except OrderError as oe:
        assert oe.msg == "Order is already complete, please start new order."
    else:
        assert False
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0



#Unit Tests for Inventory
def test_successful_update_stock_side(system_fixture):
    inventory = system_fixture.inventory
    inventory.updateStockSide("Can Coke", 1) 
    canCoke = inventory.getIngredient("can Coke")
    assert canCoke.quantity == 99

def test_successful_update_stock_servingsize_side(system_fixture):
    inventory = system_fixture.inventory
    inventory.updateStockSide("Orange Juice", 1, "small")
    orangejuice = inventory.getIngredient("Orange Juice")
    assert orangejuice.quantity == 9750

def test_fail_update_stock_wrong_servingsize_side(system_fixture):
    inventory = system_fixture.inventory
    for name in ["Tomato", "Cheddar Cheese", "Lettuce"]:
        try:
            inventory.updateStockSide(name, 1, "small")
        except InventoryError as be:
            msg = "Incorrect serving size for " + name.lower()
            assert (be.msg == msg)
        else:
            assert False

def test_successful_update_main(system_fixture):
    inventory = system_fixture.inventory
    mainIngredients = {"tomato":1, "cheddar cheese":1, "sesame bun":2}
    inventory.updateStockMain(mainIngredients)
    tomato = inventory.getIngredient("tomato")
    assert tomato.quantity == 99
    cheddar = inventory.getIngredient("cheddar cheese")
    assert cheddar.quantity == 99
    sesamebun = inventory.getIngredient("sesame bun")
    assert sesamebun.quantity == 98

# Unit Tests for Main class
def test_main_standard_order(system_fixture):
    ingred = {"Sesame Bun":2, "Tomato":3, "Lettuce":2, "Cheddar Cheese":2, "Beef":1}
    main = Main(ingred)
    inventory = system_fixture.inventory
    for name, quantity in ingred.items():
        assert main.ingredients[name] == quantity
    cost = 0
    for name, quantity in ingred.items():
        ingredient = inventory.getIngredient(name)
        cost += ingredient.price * quantity
    assert main.calculateCost(inventory) == cost
    assert str(main) == "Main Order: Ingredients List\nSesame Bun Qty: 2\nTomato Qty: 3\nLettuce Qty: 2\nCheddar Cheese Qty: 2\nBeef Qty: 1"

def test_main_empty(system_fixture):
    main = Main({})
    inventory = system_fixture.inventory
    assert main.calculateCost(inventory) == 0
    assert str(main) == "Main Order: Ingredients List"

def test_main_negative_ingredients(system_fixture):
    main = Main({"Sesame Bun":-1})
    inventory = system_fixture.inventory
    assert main.ingredients["Sesame Bun"] == -1
    assert main.calculateCost(inventory) == 0
    assert str(main) == "Main Order: Ingredients List"

def test_main_mixed_erronous_ingredients(system_fixture):
    main = Main({"Sesame Bun":-1, "Tomato":3})
    inventory = system_fixture.inventory
    assert main.ingredients["Sesame Bun"] == -1
    assert main.ingredients["Tomato"] == 3
    assert main.calculateCost(inventory) == inventory.getIngredient("Tomato").price * 3
    assert str(main) == "Main Order: Ingredients List\nTomato Qty: 3"

# Unit Tests for SideDrink class
def test_side_meal_order(system_fixture):
    side = SideDrink("Chicken Nugget", 2, "large")
    inventory = system_fixture.inventory
    assert side.name == "Chicken Nugget"
    assert side.quantity == 2
    assert side.servingSize == "large"
    assert side.calculateCost(inventory) == inventory.getIngredient("Chicken Nugget").price * 2 * inventory.getIngredient("Chicken Nugget").servingSizes["large"]
    assert str(side) == "Chicken Nugget, Qty: 2, Size: large"

def test_side_drink_order(system_fixture):
    side = SideDrink("Orange Juice", 4, "large")
    inventory = system_fixture.inventory
    assert side.name == "Orange Juice"
    assert side.quantity == 4
    assert side.servingSize == "large"
    assert side.calculateCost(inventory) == inventory.getIngredient("Orange Juice").price * 4 * inventory.getIngredient("Orange Juice").servingSizes["large"]
    assert str(side) == "Orange Juice, Qty: 4, Size: large"

def test_side_negative_order(system_fixture):
    side = SideDrink("Chicken Nugget", -1, "large")
    inventory = system_fixture.inventory
    assert side.name == "Chicken Nugget"
    assert side.quantity == -1
    assert side.servingSize == "large"
    assert side.calculateCost(inventory) == 0
    assert str(side) == ""