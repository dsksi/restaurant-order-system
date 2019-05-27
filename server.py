from flask import Flask
# from init import bootstrap_system
from backend.system import RestaurantSystem

app = Flask(__name__)

# Using persistence:
system = RestaurantSystem.loadData()

# Not using persistence
# system = bootstrap_system()
# to refresh system.dat to original test system
# system.saveData()