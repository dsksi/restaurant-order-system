from flask import render_template, request, redirect, url_for, abort
from server import app, system
from backend.system import RestaurantSystem
from backend.inventory import IngredientType
from backend.order import Order
from backend.errors import SystemError, InventoryError, OrderError
from form import Form, InventoryForm, WrapForm, BurgerForm, IngredientForm, SideDrinkForm
from threading import Timer
'''
Dedicated page for "page not found"
'''
@app.route('/404')
@app.errorhandler(404)
def page_not_found(e=None):
    return render_template('404.html'), 404

'''
Index page
'''
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form = request.form
        if 'orderID' in form:
            try:
                if form.get('orderID') == '':
                    raise SystemError("Please enter order ID")
                else:
                    orderID = int(form.get('orderID'))
                    order = system.getPaidOrderFromID(orderID)
            except SystemError as se:
                return render_template('index.html', system=system, error=se)
            else:
                return redirect(url_for('orderStatus', system=system, orderID=order.ID))           
    return render_template('index.html', system=system)

def orderTimeOut(order):
    if order.paid == False:
        try:
            system.cancelOrder(order.ID)
        except SystemError:
            print("Order already cancelled by customer.")
        else:
            print("Order " + str(order.ID) + " canceled due to timeout")
    else:
        print("Order already paid within time limit")

@app.route('/main/create')
def create():
    order = system.createOrder()
    #If order do not checkout within 20 mins, order will expire and be cancelled
    Timer(1800, orderTimeOut, [order]).start()
    return redirect(url_for('main', orderID=order.ID))

@app.route('/expired')
def expired():
    return render_template("expired.html")

@app.route('/cancel/<orderID>')
def ordercancel(orderID):
    try:
        system.cancelOrder(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
    return render_template("cancel.html")

@app.route('/completed')
def completed():
    return render_template("completed.html")

'''
Main pages
'''
@app.route('/main/<orderID>', methods=["GET", "POST"])
def main(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    if request.method == "POST":
        if "standardWrap" in request.form:
            try:
                order.addStandardWrap(system.inventory)
            except InventoryError as ie:
                # Insufficient inventory
                return render_template('main.html', order=order, werror=ie)
            else:
                return render_template('main.html', order=order, wadded='Standard Wrap')
        elif "standardBurger" in request.form:
            try:
                order.addStandardBurger(system.inventory)
            except InventoryError as ie:
                # Insufficient inventory
                return render_template('main.html', order=order, berror=ie)
            else:
                return render_template('main.html', order=order, badded='Standard Burger')
    if order.paid == True:
        return redirect(url_for("completed"))
    return render_template('main.html', order=order)


# Add main wrap order
@app.route('/wrap/<orderID>', methods=["GET", "POST"])
def wrap(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    if order.paid == True:
        return redirect(url_for("completed"))
    hasWrap = False
    hasPatty = False
    hasFilling = False
    for ingredient in system.inventory.ingredients:
        if ingredient.iType == IngredientType.WRAP:
            if ingredient.quantity > 0:
                hasWrap = True
        elif ingredient.iType == IngredientType.PATTY:
            if ingredient.quantity > 0:
                hasPatty = True
        elif ingredient.iType == IngredientType.FILLING:
            if ingredient.quantity > 0:
                hasFilling = True

    if request.method == "POST":
        form = WrapForm(request.form)
        if not form.is_valid:
            return render_template("wrap.html", order=order, form=form, system=system, iType=IngredientType,
                                    hasWrap=hasWrap, hasPatty=hasPatty, hasFilling=hasFilling)
        ingredients = {}
        for name, quantity in request.form.items():
            if quantity != '' and quantity != '0':
                ingredients[name] = int(quantity)
        order.addWrapMain(system.inventory, ingredients)
        return render_template("wrap.html", order=order, system=system, added=True, iType=IngredientType,
                                hasWrap=hasWrap, hasPatty=hasPatty, hasFilling=hasFilling)
    return render_template('wrap.html', order=order, system=system, iType=IngredientType,
                            hasWrap=hasWrap, hasPatty=hasPatty, hasFilling=hasFilling)

# Add main burger order
@app.route('/burger/<orderID>', methods=["GET", "POST"])
def burger(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    if order.paid == True:
        return redirect(url_for("completed"))
    hasPatty = False
    hasBun = False
    hasFilling = False
    for ingredient in system.inventory.ingredients:
        if ingredient.iType == IngredientType.BURGERBUN:
            if ingredient.quantity > 0:
                hasBun = True
        elif ingredient.iType == IngredientType.PATTY:
            if ingredient.quantity > 0:
                hasPatty = True
        elif ingredient.iType == IngredientType.FILLING:
            if ingredient.quantity > 0:
                hasFilling = True

    if request.method == "POST":
        form = BurgerForm(request.form)
        if not form.is_valid:
            return render_template("burger.html", order=order, form=form, system=system, iType=IngredientType,
                                    hasPatty=hasPatty, hasBun=hasBun, hasFilling=hasFilling)
        ingredients = {}
        for name, quantity in request.form.items():
            if quantity != '' and quantity != '0':
                ingredients[name] = int(quantity)
        order.addBurgerMain(system.inventory, ingredients)
        return render_template("burger.html", order=order, system=system, added=True, iType=IngredientType,
                                hasPatty=hasPatty, hasBun=hasBun, hasFilling=hasFilling)
    return render_template('burger.html', order=order, system=system, iType=IngredientType, hasPatty=hasPatty, 
                            hasBun=hasBun, hasFilling=hasFilling)

'''
Side and drink page
'''
# Add drink and side orders
@app.route('/sidedrink/<orderID>', methods=["GET", "POST"])
def sidedrink(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    if order.paid == True:
        return redirect(url_for("completed"))    
    has = {IngredientType.DRINK:False, IngredientType.SIDE:False}
    for ingredient in system.inventory.ingredients:
        if ingredient.iType in has:
            if 'regular' in ingredient.servingSizes and ingredient.quantity > 0:
                has[ingredient.iType] = True
            elif 'small' in ingredient.servingSizes and ingredient.quantity > ingredient.servingSizes['small']:
                has[ingredient.iType] = True

    if request.method == "POST":
        form = SideDrinkForm(request.form)
        if not form.is_valid:
            return render_template('sidedrink.html', order=order, has=has, form=form, system=system, iType=IngredientType)
        added = {}
        for name, values in form.outputs.items():
            ingredient = system.inventory.getIngredient(name)
            if ingredient.iType == IngredientType.DRINK:
                added["drink"] = True
                order.addDrink(system.inventory, name, values[1], values[0])
            elif ingredient.iType == IngredientType.SIDE:
                order.addSide(system.inventory, name, values[1], values[0])
                added["side"] = True
        return render_template('sidedrink.html', order=order, system=system, iType=IngredientType, has=has, added=added) 
    return render_template('sidedrink.html', order=order, system=system, iType=IngredientType, has=has)

'''
Order pages
'''
@app.route('/<orderID>/review')
def reviewOrder(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    if order.paid == True:
        return redirect(url_for("completed"))
    price = order.calculateTotalPrice(system.inventory)
    return render_template('revieworder.html', system=system, order=order, price=round(price,2))

# Check order status
@app.route('/<orderID>/status')
def orderStatus(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    return render_template('orderstatus.html', order=order, system=system)

@app.route('/<orderID>/checkout')
def checkOut(orderID):
    try:
        order = system.getOrderFromID(int(orderID))
    except:
        if int(orderID) < system.orderIDCounter:
            return redirect(url_for("expired"))
        return redirect(url_for('page_not_found'))
    if order.paid == False:
        try:
            system.checkout(int(orderID))
        except OrderError as oe:
            return render_template('revieworder.html', order=order, error=oe)
        system.saveData()   # persistence
    #order is already paid
    return render_template('orderstatus.html', system=system, order=order)

'''
Staff pages
'''

# Active order
@app.route('/staff', methods=["GET", "POST"])
def staff():
    orders = system.activeOrders
    if request.method == "POST":
        orderID = int(request.form.get("prepared"))
        system.orderPrepared(orderID)
        system.saveData()   # persistence
        orders = system.activeOrders
        return render_template('staff.html', orders=orders, staff=True)
    return render_template('staff.html', orders=orders, staff=True)

# Service order
@app.route('/staff/<orderID>', methods=["GET", "POST"])
def serviceOrder(orderID):
    try:
        order = system.getPaidOrderFromID(int(orderID))
    except:
        return redirect(url_for('page_not_found'))
    if request.method == "POST":
        if order.prepared == False:
            system.orderPrepared(order.ID)
            system.saveData() # persistence
            return redirect(url_for('staff'))
        else:
           return render_template('staffserviceorder.html', inventory=system.inventory, order=order, staff=True) 
    return render_template('staffserviceorder.html', inventory=system.inventory, order=order, staff=True)

# Staff - update inventory
@app.route('/staff/inventory', methods=["GET", "POST"])
def inventory():
    has = {}
    for ingType in IngredientType:
        has[ingType] = False
    for ingredient in system.inventory.ingredients:
        has[ingredient.iType] = True
    if request.method == "POST":
        form = InventoryForm(request.form)
        if not form.is_valid:
            return render_template('inventory.html', iType=IngredientType, has=has, form=form, system=system, staff=True)
        
        ingredients = {}
        for name, quantity in request.form.items():
            if quantity != '' and quantity != '0':
                ingredients[name] = int(quantity)
        system.inventory.updateInventory(ingredients)
        system.saveData() # persistence
        return render_template('inventory.html', iType=IngredientType, has=has, system=system, staff=True, success=True)
    if len(system.inventory.ingredients) == 0:
        return render_template('inventory.html', iType=IngredientType, has=has, system=system, staff=True, noIngredients=True)
    return render_template('inventory.html', iType=IngredientType, has=has, system=system, staff=True)

#Add new ingredient to inventory
@app.route('/staff/add', methods=["GET", "POST"])
def addIngredient():
    if request.method == "POST":
        form = IngredientForm(request.form)
        if not form.is_valid:
            return render_template('addingredient.html', form=form, IngredientType=IngredientType, staff=True)
        name = form.outputs['name']
        quantity = form.outputs['quantity']
        price = form.outputs['price']
        ingType = form.outputs['type']
        unit = form.outputs['unit']
        servingSizes = {}
        size = form.outputs['size']
        if size == "regular":
            servingSizes['regular'] = 1
        elif size == "smlSize":
            servingSizes['small'] = form.outputs['sQty']
            servingSizes['medium'] = form.outputs['mQty']
            servingSizes['large'] = form.outputs['lQty']
        system.inventory.addIngredient(name, price, quantity, ingType, servingSizes, unit)
        system.saveData() # persistence
        return render_template('addingredient.html', success=name, IngredientType=IngredientType, staff=True)
    return render_template('addingredient.html', IngredientType=IngredientType, staff=True)