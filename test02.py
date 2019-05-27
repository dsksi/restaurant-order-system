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
test02: Review order details and checkout - US1.4, 1.5, 1.6, 1.7
'''
### User Story 1.4 - Review Order ###
def test_displayOrder_pending(system_fixture):
    order = system_fixture.createOrder()
    inventory = system_fixture.inventory
    parts = []
    parts.append("====================================")
    parts.append("Order ID {}".format(order.ID))
    parts.append("Order status:")
    parts.append("- Pending: unpaid")
    cost = order.calculateTotalPrice(inventory)
    for main in order.mainOrders:
        parts.append("Main order")
        parts.append(main.__str__())
    for sideDrink in order.sidesAndDrinks:
        parts.append("Side order")
        parts.append(sideDrink.__str__())
    parts.append("Total Fee: ${}".format(cost))
    parts.append("====================================")
    final = "\n".join(parts)
    
    assert final == order.displayOrder(inventory)

### User Story 1.5 - Checkout ###
def test_success_submit_and_pay(system_fixture):
    order = system_fixture.createOrder()
    inventory = system_fixture.inventory
    #check order initialised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":1,"sesame bun":2}
    msg = order.addBurgerMain(inventory, ingredients)
    assert len(order.mainOrders) == 1
    order.submitAndPay(True)
    assert order.paid == True

def test_fail_submit_and_pay_empty_order(system_fixture):
    order = system_fixture.createOrder()
    #check order initialised in correct state
    inventory = system_fixture.inventory
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    try:
        order.submitAndPay(True)
    except OrderError as oe:
        assert oe.msg == "Must order before checkout"

def test_fail_submit_and_pay_unsuccessful_payment(system_fixture):
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
    try:
        order.submitAndPay(False)
    except OrderError as oe:
        assert oe.msg == "Payment unsuccessful"

def test_checkout_successful(system_fixture):
    order = system_fixture.createOrder()
    order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    assert len(system_fixture.pendingOrders) == 1
    assert len(system_fixture.activeOrders) == 0
    assert len(system_fixture.finishedOrders) == 0
    system_fixture.checkout(1)
    assert len(system_fixture.pendingOrders) == 0
    assert len(system_fixture.activeOrders) == 1
    assert len(system_fixture.finishedOrders) == 0
    assert system_fixture.getOrderFromID(1) == system_fixture.activeOrders[0]

def test_checkout_nonexistentID(system_fixture):
    try:
        system_fixture.checkout(1)
    except SystemError as se:
        assert se.msg == "Incorrect order ID entered."
    else:
        assert False

def test_checkout_activeID(system_fixture):
    order = system_fixture.createOrder()
    order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    system_fixture.checkout(1)
    try:
        system_fixture.checkout(1)
    except SystemError as se:
        assert se.msg == "Order is not pending."
    else:
        assert False

def test_checkout_finishedID(system_fixture):
    order = system_fixture.createOrder()
    order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    system_fixture.checkout(1)
    system_fixture.orderPrepared(1)
    try:
        system_fixture.checkout(1)
    except SystemError as se:
        assert se.msg == "Order is not pending."
    else:
        assert False

def test_checkout_empty_order(system_fixture):
    order = system_fixture.createOrder()
    assert len(system_fixture.pendingOrders) == 1
    assert order.ID == 1
    try:
        system_fixture.checkout(1)
    except OrderError as oe:
        assert oe.msg == "Must order before checkout"
    else:
        assert False
    finally:
        assert len(system_fixture.activeOrders) == 0
        assert len(system_fixture.pendingOrders) == 1

### User Story 1.6 - Obtain order ID ###
def test_displayOrder_active(system_fixture):
    order = system_fixture.createOrder()
    inventory = system_fixture.inventory
    order.addSide(inventory, "chicken nugget", 2, "small")
    ingredients = {"tomato":1, "cheddar cheese":1,"chicken":1,"flatbread":1}
    order.addWrapMain(inventory, ingredients)
    order.submitAndPay(True)

    parts = []
    parts.append("====================================")
    parts.append("Order ID {}".format(order.ID))
    parts.append("Order status:")
    parts.append("- Active: in service")
    cost = order.calculateTotalPrice(inventory)
    for main in order.mainOrders:
        parts.append("Main order")
        parts.append(main.__str__())
    for sideDrink in order.sidesAndDrinks:
        parts.append("Side order")
        parts.append(sideDrink.__str__())
    parts.append("Total Fee: ${}".format(cost))
    parts.append("====================================")
    final = "\n".join(parts)
    
    assert final == order.displayOrder(inventory)

### User Story 1.7 - Check order status ###
def test_seeOrderStatusFromID_notPrepared(system_fixture):
    # tests pending and active orders
    for i in range(5):
        system_fixture.createOrder()
        system_fixture.getOrderFromID(i+1).addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    for i in range(3):
         system_fixture.checkout(i+1)
    system_fixture.orderPrepared(1)
    assert system_fixture.seeOrderStatusFromID(5) == "Your order is not paid."
    assert system_fixture.seeOrderStatusFromID(3) == "Your order is being prepared."
    
def test_seeOrderStatusFromID_prepared(system_fixture):
    for i in range(5):
        system_fixture.createOrder()
        system_fixture.getOrderFromID(i+1).addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    for i in range(3):
         system_fixture.checkout(i+1)
    system_fixture.orderPrepared(1)
    assert system_fixture.seeOrderStatusFromID(1) == "Your order is ready to be collected."

def test_seeOrderStatusFromID_invalid(system_fixture):
    try:
        system_fixture.seeOrderStatusFromID(1)
    except SystemError as se:
        assert se.msg == "Incorrect order ID entered."
    else:
        assert False

def test_displayOrder_finished(system_fixture):
    order = system_fixture.createOrder()
    inventory = system_fixture.inventory
    order.addSide(inventory, "chicken nugget", 2, "small")
    ingredients = {"tomato":1, "cheddar cheese":1,"chicken":1,"flatbread":1}
    order.addWrapMain(inventory, ingredients)
    order.submitAndPay(True)
    order.updatePrepared()
    parts = []
    parts.append("====================================")
    parts.append("Order ID {}".format(order.ID))
    parts.append("Order status:")
    parts.append("- Finished: order prepared")
    cost = order.calculateTotalPrice(inventory)
    for main in order.mainOrders:
        parts.append("Main order")
        parts.append(main.__str__())
    for sideDrink in order.sidesAndDrinks:
        parts.append("Side order")
        parts.append(sideDrink.__str__())
    parts.append("Total Fee: ${}".format(cost))
    parts.append("====================================")
    final = "\n".join(parts)
    
    assert final == order.displayOrder(inventory)


# Unit Tests for System
def test_getOrderFromID_validID(system_fixture):
    system_fixture.createOrder()
    order2 = system_fixture.createOrder()
    order2.addBurgerMain(system_fixture.inventory, {"Beef": 1, "Muffin Bun": 2})
    order2.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    system_fixture.createOrder()
    assert len(system_fixture.pendingOrders) == 3
    order = system_fixture.getOrderFromID(2)
    assert order == system_fixture.pendingOrders[1]
    assert len(order.mainOrders) == 1
    assert order.mainOrders[0].ingredients == {"Beef": 1, "Muffin Bun": 2}
    assert len(order.sidesAndDrinks) == 1
    assert order.sidesAndDrinks[0].name == "Can Fanta"

def test_getOrderFromID_invalidID(system_fixture):
    system_fixture.createOrder()
    assert len(system_fixture.pendingOrders) == 1
    try:
        system_fixture.getOrderFromID(6) == None
    except SystemError as se:
        assert se.msg == "Incorrect order ID entered."

def test_success_getPaidOrderFromID_active(system_fixture):
    for i in range(3):
        order = system_fixture.createOrder()
        order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    order4 = system_fixture.createOrder()
    order4.addBurgerMain(system_fixture.inventory, {"Beef": 1, "Muffin Bun": 2})
    assert len(system_fixture.pendingOrders) == 4
    for i in range(4):
        system_fixture.checkout(i+1)
    order = system_fixture.getPaidOrderFromID(2)
    assert order == system_fixture.activeOrders[1]
    assert len(order.sidesAndDrinks) == 1
    assert len(order.mainOrders) == 0
    order = system_fixture.getPaidOrderFromID(4)
    assert order == system_fixture.activeOrders[3]
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

def test_success_getPaidOrderFromID_finished(system_fixture):
    for i in range(3):
        order = system_fixture.createOrder()
        order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    order4 = system_fixture.createOrder()
    order4.addBurgerMain(system_fixture.inventory, {"Beef": 1, "Muffin Bun": 2})
    assert len(system_fixture.pendingOrders) == 4
    for i in range(4):
        system_fixture.checkout(i+1)
    system_fixture.orderPrepared(2)
    system_fixture.orderPrepared(4)
    order = system_fixture.getPaidOrderFromID(2)
    assert order == system_fixture.finishedOrders[0]
    assert len(order.sidesAndDrinks) == 1
    assert len(order.mainOrders) == 0
    order = system_fixture.getPaidOrderFromID(4)
    assert order == system_fixture.finishedOrders[1]
    assert len(order.mainOrders) == 1
    assert len(order.sidesAndDrinks) == 0

def test_fail_getPaidOrderFromID_pending(system_fixture):
    order = system_fixture.createOrder()
    assert len(system_fixture.pendingOrders) == 1
    assert order.ID == 1
    try:
        system_fixture.getPaidOrderFromID(1)
    except SystemError as se:
        assert se.msg == "Incorrect order ID entered."
    else:
        assert False

def test_fail_getPaidOrderFromID_nonexistent_ID(system_fixture):
    assert len(system_fixture.pendingOrders) == 0
    try:
        system_fixture.getPaidOrderFromID(1)
    except SystemError as se:
        assert se.msg == "Incorrect order ID entered."
    else:
        assert False

def test_success_cancel_order_with_main(system_fixture):
    order = system_fixture.createOrder()
    inventory = system_fixture.inventory
    #check order initialised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    ingredients = {"tomato":1, "cheddar cheese":1,"beef":1,"sesame bun":2}
    msg = order.addBurgerMain(inventory, ingredients)
    assert len(order.mainOrders) == 1
    for name, quantity in ingredients.items():
        assert order.mainOrders[0].ingredients[name] == quantity
    assert order.calculateTotalPrice(inventory) == 9    
    for name, quantity in ingredients.items():
        ingredient = inventory.getIngredient(name)
        assert ingredient.quantity == (100 - quantity)
    assert msg == "Main added to order"

    msg2 = order.cancel(inventory)
    assert msg2 == "Order cancelled"
    for name, quantity in ingredients.items():
        ingredient = inventory.getIngredient(name)
        assert ingredient.quantity == 100 

def test_success_cancel_order_with_side(system_fixture):
    order = system_fixture.createOrder()
    inventory = system_fixture.inventory
    #check order initalised in correct state
    assert order.ID == 1
    assert order.prepared == False
    assert order.paid == False
    assert len(order.mainOrders) == 0
    assert len(order.sidesAndDrinks) == 0

    msg = order.addSide(inventory, "chicken nugget", 2, "small")
    assert msg == "Sides added to order"
    assert len(order.sidesAndDrinks) == 1
    ingredient = inventory.getIngredient("chicken nugget")
    assert ingredient.quantity == (1000 - 6)
    assert order.calculateTotalPrice(inventory) == 6

    msg2 = order.cancel(inventory)
    assert msg2 == "Order cancelled"
    ingredient = inventory.getIngredient("chicken nugget")
    assert ingredient.quantity == 1000

def test_cancelOrder_success_pending(system_fixture):
    system_fixture.createOrder()
    assert len(system_fixture.pendingOrders) == 1
    system_fixture.cancelOrder(1)
    assert len(system_fixture.pendingOrders) == 0

def test_cancelOrder_fail_active(system_fixture):
    order = system_fixture.createOrder()
    order.addDrink(system_fixture.inventory, "Can Fanta", 1, "regular")
    assert len(system_fixture.pendingOrders) == 1
    system_fixture.checkout(1)
    assert len(system_fixture.pendingOrders) == 0
    assert len(system_fixture.activeOrders) == 1
    try:
        system_fixture.cancelOrder(1)
    except SystemError as se:
        assert se.msg == "Order is not pending."
    else:
        assert False