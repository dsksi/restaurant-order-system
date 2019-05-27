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
test04: Staff - maintain inventory - US3.1, 3.2, 3.3
'''
### User Story 3.2 - Update inventory levels ###
def test_successful_update_inventory_add_single_ingredient(system_fixture):
    ingredients = {"tomato": 10}
    inventory = system_fixture.inventory
    tomato = inventory.getIngredient("tomato")
    assert tomato.quantity == 100
    cheddar = inventory.getIngredient("cheddar cheese")
    assert cheddar.quantity == 100
    inventory.updateInventory(ingredients)
    assert tomato.quantity == 110
    assert cheddar.quantity == 100

def test_successful_update_inventory_add_ingredients(system_fixture):
    ingredients = {"tomato": 10, "cheddar cheese": 15, "sesame bun": 100, "chicken nugget":10, "orange juice":100}
    inventory = system_fixture.inventory
    tomato = inventory.getIngredient("tomato")
    assert tomato.quantity == 100
    cheddar = inventory.getIngredient("cheddar cheese")
    assert cheddar.quantity == 100
    sesamebun = inventory.getIngredient("sesame bun")
    assert sesamebun.quantity == 100
    muffinbun = inventory.getIngredient("muffin bun")
    assert muffinbun.quantity == 100
    orange_juice = inventory.getIngredient("orange juice")
    assert orange_juice.quantity == 10000
    chicken_nuggets = inventory.getIngredient("chicken nugget")
    assert chicken_nuggets.quantity == 1000
    inventory.updateInventory(ingredients)
    assert tomato.quantity == 110
    assert cheddar.quantity == 115
    assert sesamebun.quantity == 200
    assert muffinbun.quantity == 100
    assert orange_juice.quantity == 10100
    assert chicken_nuggets.quantity == 1010

def test_successful_update_inventory_remove_single_ingredient(system_fixture):
    ingredients = {"tomato": -10}
    inventory = system_fixture.inventory
    tomato = inventory.getIngredient("tomato")
    assert tomato.quantity == 100
    cheddar = inventory.getIngredient("cheddar cheese")
    assert cheddar.quantity == 100
    inventory.updateInventory(ingredients)
    assert tomato.quantity == 90
    assert cheddar.quantity == 100

def test_successful_update_inventory_remove_ingredients(system_fixture):
    ingredients = {"tomato": -10, "cheddar cheese": -15, "sesame bun": -100, "chicken nugget":-1000, "orange juice":-100}
    inventory = system_fixture.inventory
    tomato = inventory.getIngredient("tomato")
    assert tomato.quantity == 100
    cheddar = inventory.getIngredient("cheddar cheese")
    assert cheddar.quantity == 100
    sesamebun = inventory.getIngredient("sesame bun")
    assert sesamebun.quantity == 100
    muffinbun = inventory.getIngredient("muffin bun")
    assert muffinbun.quantity == 100
    orange_juice = inventory.getIngredient("orange juice")
    assert orange_juice.quantity == 10000
    chicken_nuggets = inventory.getIngredient("chicken nugget")
    assert chicken_nuggets.quantity == 1000
    inventory.updateInventory(ingredients)
    assert tomato.quantity == 90
    assert cheddar.quantity == 85
    assert sesamebun.quantity == 0
    assert muffinbun.quantity == 100
    assert orange_juice.quantity == 9900
    assert chicken_nuggets.quantity == 0

def test_fail_update_inventory_remove_exceeding_stock(system_fixture):
    ingredients = {"tomato": -110}
    inventory = system_fixture.inventory
    tomato = inventory.getIngredient("tomato")
    assert tomato.quantity == 100
    try:
        inventory.updateInventory(ingredients)
    except InventoryError as ie:
        assert ie.msg == "Insufficient stock for tomato"
    else:
        assert False

### User Story 3.1 - View current inventory levels ###
def test_successful_get_ingredient_case_insensitive(system_fixture):
    inventory = system_fixture.inventory
    for name in ["tomato", "cheddar cheese", "lettuce", "swiss cheese"]:
        ingredient = inventory.getIngredient(name)
        assert ingredient.name.lower() == name.lower()

    for name in ["SESAME BUN", "MUFFIN BUN"]:
        ingredient = inventory.getIngredient(name)
        assert ingredient.name.lower() == name.lower()

def test_fail_get_ingredient_nonexistent(system_fixture):
    inventory = system_fixture.inventory
    for name in ["potato", "cucumber", "banana"]:
        try:    
            ingredient = inventory.getIngredient(name)
        except InventoryError as be:
            assert be.msg == (name.capitalize() + " does not exist")
        else:
            assert False

### User Story 3.3 - Add new ingredients ###
def test_success_add_new_ingredient(system_fixture):
    inventory = system_fixture.inventory
    name = "chocolate icecream"
    icecreamSize = {"small":100, "medium":200, "large":300}
    try:
        ingredient = inventory.getIngredient(name)
    except InventoryError as ie:
        assert ie.msg == "Chocolate icecream does not exist"
    else:
        assert False
    inventory.addIngredient(name, 0.03, 10000, IngredientType.SIDE, icecreamSize, "g")
    ingredient = inventory.getIngredient(name)
    assert ingredient.name == name
    assert ingredient.servingSizes == icecreamSize
    assert ingredient.unit == "g"

def test_success_add_ingredient_drink_ml(system_fixture):
    inventory = system_fixture.inventory
    name = "chocolate milk"
    drinkSize = {"small":100, "medium":200, "large":300}
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name) 
    inventory.addIngredient(name, 0.03, 10000, IngredientType.DRINK, drinkSize, "ml")
    ingredient = inventory.getIngredient(name)
    assert ingredient.name == name
    assert ingredient.servingSizes == drinkSize
    assert ingredient.unit == "ml"
    assert ingredient.price == 0.03
    assert ingredient.quantity == 10000

def test_fail_add_ingredient_wrong_unit_ml(system_fixture):
    inventory = system_fixture.inventory
    name = "chocolate icecream"
    icecreamSize = {"small":100, "medium":200, "large":300}
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name) 
    try:
        inventory.addIngredient(name, 0.03, 10000, IngredientType.SIDE, icecreamSize, "ml")
    except InventoryError as ie:
        assert ie.msg == "Chocolate icecream must be type drink to be stored in ml"
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name)

def test_success_add_ingredient_regular_unit(system_fixture):
    inventory = system_fixture.inventory
    name = "cucumber"
    regularSize = {"regular":1}
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name) 
    inventory.addIngredient(name, 1, 100, IngredientType.FILLING, regularSize)
    ingredient = inventory.getIngredient(name)
    assert ingredient.name == name
    assert ingredient.price == 1
    assert ingredient.quantity == 100
    assert ingredient.servingSizes == regularSize
    assert ingredient.unit == "unit" 

def test_fail_add_ingredient_regular_with_wrong_unit(system_fixture):
    inventory = system_fixture.inventory
    name = "cucumber"
    regularSize = {"regular":1}
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name) 
    try:
        inventory.addIngredient(name, 1, 100, IngredientType.FILLING, regularSize, "g")
    except InventoryError as ie:
        assert ie.msg == "Filling must be stored as unit"
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name)

def test_fail_add_ingredient_invalid_unit(system_fixture):
    inventory = system_fixture.inventory
    name = "chocolate icecream"
    icecreamSize = {"small":100, "medium":200, "large":300}
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name) 
    try:
        inventory.addIngredient(name, 0.03, 10000, IngredientType.SIDE, icecreamSize, "mm")
    except InventoryError as ie:
        assert ie.msg == "Please enter valid unit"
    with pytest.raises(InventoryError):
        ingredient = inventory.getIngredient(name)