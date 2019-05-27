from backend.order import Order
from backend.inventory import Inventory
from backend.errors import SystemError
import pickle
class RestaurantSystem:
    def __init__(self):
        self._inventory = Inventory()
        self._orderIDCounter = 1
        self._pendingOrders = []
        self._activeOrders = []
        self._finishedOrders = []

    @property
    def inventory(self):
        return self._inventory

    @property
    def activeOrders(self):
        return self._activeOrders

    @property
    def pendingOrders(self):
        return self._pendingOrders

    @property
    def finishedOrders(self):
        return self._finishedOrders

    @property
    def orderIDCounter(self):
        return self._orderIDCounter

    def createOrder(self):
        order = Order(self._orderIDCounter)
        self._orderIDCounter += 1
        self._pendingOrders.append(order)
        return order

    def getOrderFromID(self, ID):
        for orderList in [self._pendingOrders, self._activeOrders, self._finishedOrders]:
            for order in orderList:
                if order.ID == ID:
                    return order
        raise SystemError("Incorrect order ID entered.")

    def getPaidOrderFromID(self, ID):
        for orderList in [self._activeOrders, self._finishedOrders]:
            for order in orderList:
                if order.ID == ID:
                    return order
        raise SystemError("Incorrect order ID entered.")

    def seeOrderStatusFromID(self, ID):
        # returns boolean value for if order is prepared
        order = self.getOrderFromID(ID)
        if order.paid == False:
            return "Your order is not paid."
        else:
            if order.prepared == True:
                return "Your order is ready to be collected."
            else:
                return "Your order is being prepared."

    def orderPrepared(self, ID):
        order = self.getOrderFromID(ID)
        if order not in self._activeOrders:
            raise SystemError("Order is not active.")
        else:
            order.updatePrepared()
            self._activeOrders.remove(order)
            self._finishedOrders.append(order)

    def checkout(self, ID):
        #calls external payment system
        #returns bool to indicate whether payment was successful
        order = self.getOrderFromID(ID)
        if order not in self._pendingOrders:
            raise SystemError("Order is not pending.")
        else:
            payStatus = True
            order.submitAndPay(payStatus)
            self._pendingOrders.remove(order)
            self._activeOrders.append(order)

    def cancelOrder(self, ID):
        order = self.getOrderFromID(ID)
        if order not in self._pendingOrders:
            raise SystemError("Order is not pending.")
        else:
            order.cancel(self._inventory)
            self._pendingOrders.remove(order)

    def displayActiveOrders(self):
        parts = []
        parts.append("ACTIVE ORDERS")
        for order in self.activeOrders:
            parts.append(order.displayOrder(self.inventory))
        final = "\n".join(parts)
        return final
    
    @classmethod
    def loadData(cls):
        try:
            with open('system.dat', 'rb') as file:
                system = pickle.load(file)
        except IOError:
            system = RestaurantSystem()
        return system
    
    def saveData(self):
        with open('system.dat', 'wb') as file:
            pickle.dump(self, file)
