from backend.system import RestaurantSystem
from backend.errors import SystemError, OrderError, InventoryError
from backend.order import Order
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
test03: Staff - service online orders - US2.1, 2.2
'''
### User Story 2.1 - View current orders ###
def test_display_active_order(system_fixture):
    order = system_fixture.createOrder()
    order.addBurgerMain(system_fixture.inventory, {"Beef": 1, "Muffin Bun": 2})
    order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    parts = []
    system_fixture.checkout(1) 
    parts.append("ACTIVE ORDERS")
    parts.append(order.displayOrder(system_fixture.inventory))
    final = "\n".join(parts)
    test = system_fixture.displayActiveOrders()  
    assert final == test

### User Story 2.2 - Update order status ###
def test_success_order_prepared(system_fixture):
    order = system_fixture.createOrder()
    #check order initialised in correct state
    inventory = system_fixture.inventory
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":1,"sesame bun":2}
    msg = order.addBurgerMain(inventory, ingredients)
    assert len(order.mainOrders) == 1
    order.submitAndPay(True)
    order.updatePrepared()
    assert order.prepared == True

def test_orderPrepared_successful(system_fixture):
    for i in range(5):
        system_fixture.createOrder()
        system_fixture.getOrderFromID(i+1).addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    for i in range(3):
        system_fixture.checkout(i+1)
    assert len(system_fixture.pendingOrders) == 2
    assert len(system_fixture.activeOrders) == 3
    assert len(system_fixture.finishedOrders) == 0
    assert system_fixture.seeOrderStatusFromID(1) == "Your order is being prepared."
    system_fixture.orderPrepared(1)
    assert len(system_fixture.pendingOrders) == 2
    assert len(system_fixture.activeOrders) == 2
    assert len(system_fixture.finishedOrders) == 1
    assert system_fixture.getOrderFromID(1) == system_fixture.finishedOrders[0]
    assert system_fixture.seeOrderStatusFromID(1) == "Your order is ready to be collected." 
    
def test_orderPrepared_nonexistentID(system_fixture):
    try:
        system_fixture.orderPrepared(1)
    except SystemError as se:
        assert se.msg == "Incorrect order ID entered."
    else:
        assert False

def test_orderPrepared_pendingID(system_fixture):
    system_fixture.createOrder()
    try:
        system_fixture.orderPrepared(1)
    except SystemError as se:
        assert se.msg == "Order is not active."
    else:
        assert False