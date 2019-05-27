from abc import ABC, abstractmethod
from server import system
from backend.system import RestaurantSystem
from backend.errors import OrderError, InventoryError
from backend.inventory import IngredientType

'''
ERRORS
'''
class ParseError(Exception):
    '''
    Raised when a form cannot be parsed correctly or fails validation
    '''
    pass



'''
FORMS
'''
class Form(ABC):

    def __init__(self, form):
        # Fields of the form
        # Pass in validators which is a list of validator
        self._fields = []
        # Errors not specific to a single field
        self._other_errors = {}
        for name, quantity in form.items():
            if quantity != '' and quantity != '0':
                tmp = Field(name, [PositiveInput(name), SufficientStock(name)])
                self._fields.append(tmp)
        self._parse(form)

    @property
    def fields(self):
        return self._fields

    @property
    def otherErrors(self):
        return self._other_errors

    @abstractmethod
    def _parse(self, form):
        '''
        Interprets form input from user and records any errors in the input
            - This may also perform operations such as converting a string into a date object
        '''
        pass

    def get_raw_data(self, field_name):
        '''
        returns the user's input for the specified field,
        but returns an empty string if the field does not exist
        '''
        field = self._field(field_name)
        if not field:
            return ''

        return field.raw_data or ''
 
    def get_error(self, field_name):
        '''
        returns the error for the specified field, returns an empty string
        if the field does not exist or if the field does not have any errors
        '''
        field = self._field(field_name)
        
        if not field:
            return self._other_errors.get(field_name) or ''
        return field.error or ''

    def has_error(self, field_name):
        return self.get_error(field_name) is not ''

    def _field(self, field_name):
        '''
        find and return the field object matching with the specified field name,
        if no matching field was found, then return None
        '''
        return next((field for field in self._fields if field.name == field_name), None)

    @property
    def is_valid(self):
        '''
        returns true if the form input has no errors, false otherwise
        '''
        if len(self._other_errors) > 0:
            return False

        return all(field.is_valid for field in self._fields)

# Form for burger order
class BurgerForm(Form):
    def __init__(self, form):
        return super(BurgerForm, self).__init__(form)

    def _parse(self, form):
        ingredients = {}
        for field in self._fields:
            field.parse(form.get(field.name))

        # Extra validation rules
        # Burger is valid with correct number of burger buns

        ingredients = {}
        for field in self._fields:
            quantity = form.get(field.name)
            try:
                ingredients[field.name] = int(quantity)
            except ValueError:
                pass
        try:
            system.inventory.checkBunNumber(ingredients)
        except OrderError as oe:
            self._other_errors['bun'] = oe.msg
        
        try:
            system.inventory.checkOnlyBurgerOrWrap(ingredients)
        except OrderError as oe:
            self._other_errors['onlyOne'] = oe.msg
        
# Form for wrap order
class WrapForm(Form):
    def __init__(self, form):
        super(WrapForm, self).__init__(form)

    def _parse(self, form):

        for field in self._fields:
            field.parse(form.get(field.name))

        ingredients = {}
        for field in self._fields:
            quantity = form.get(field.name)
            if quantity != None:
                try:
                    ingredients[field.name] = int(quantity)
                except ValueError:
                    pass
    # Extra validation rules
    # Wrap is valid with only one wrap
    
        try:
            system.inventory.checkOnlyOneWrap(ingredients)
        except OrderError as oe:
            self._other_errors['oneWrap'] = oe.msg
        
        try:
            system.inventory.checkOnlyBurgerOrWrap(ingredients)
        except OrderError as oe:
            self._other_errors['onlyOne'] = oe.msg
        

# Form for updating inventory stock for ingredients
class InventoryForm(Form):
    def __init__(self, form):
        self._fields = []
        # Errors not specific to a single field
        self._other_errors = {}
        for name, quantity in form.items():
            if quantity != '' and quantity != '0':
                try:
                    val = int(quantity)                    
                except ValueError:
                    self._other_errors['quantity'] = 'Can not enter non-integer quantity'
                else:
                    if val < 0:
                        tmp = Field(name, [MaintainStock(name, 'Insufficient stock for ')])
                        self._fields.append(tmp)

        self._parse(form)
    
    def _parse(self, form):
        for field in self._fields:
            field.parse(form.get(field.name))


# Form for adding new ingredient
class IngredientForm(Form):
    
    def __init__(self, form):
        self._fields = []
        # Errors not specific to a single field
        self._other_errors = {}
        self._outputs = {}
        self._parse(form)
        

    def _parse(self, form):
        # process ingredient name:
        name = form.get("name", None)
        validName = True
        if any ([name == "", name == None]):
            self._other_errors['name'] = "Please enter ingredient name"
            validName = False
    
        if validName == True:
            for char in name:
                if not char.isalpha() and char != " ":
                    self._other_errors['name'] = "Please enter valid ingredient name"
                    validName = False
                    break
        if validName == True:
            try:
                ingredient = system.inventory.getIngredient(name)
            except InventoryError:
                self._outputs['name'] = name.lower()
            else:
                self._other_errors['name'] = "Ingredient is already in inventory"
                return
                
        # process ingredient price:
        price = form.get("price", None)
        if any ([price == "", price == "0", price == None]):
            self._other_errors['price'] = "Please enter ingredient price"
        else:
            try:
                oPrice = float(price)
                if oPrice <= 0 or oPrice > 30:
                    raise ValueError
            except ValueError:
                self._other_errors['price'] = "Please enter valid ingredient price"
            else:
                self._outputs['price'] = oPrice

        # process ingredient quantity:
        quantity = form.get("quantity", None)

        if any ([quantity == None, quantity == "", quantity == "0"]):
            self._outputs['quantity'] = 0
        else:
            try:
                oQty = int(quantity)
                if oQty < 0:
                    raise ValueError
            except ValueError:
                self._other_errors['quantity'] = "Please enter valid ingredient quantity"
            else:
                self._outputs['quantity'] = oQty
    
        # process ingredient type:
        ingType = form.get("type", None)
        try:
            actualType = IngredientType(int(ingType))
            if actualType not in IngredientType:
                raise ValueError
        except: 
            self._other_errors['type'] = "Please enter valid ingredient type"
        else:
            self._outputs['type'] = actualType

        # process ingredient serving size:
        size = form.get("size", None)
        smlSize = False
        if all ([size == None, size != "regular", size != "smlSize"]):
            self._other_errors['size'] = "Please enter valid serving size"
        else:
            if size != "regular":
                allowableType = [IngredientType.SIDE, IngredientType.DRINK]
                if actualType and actualType in allowableType:
                    smlSize = True
                    self._outputs['size'] = "smlSize"
                else:
                    self._other_errors['type'] = "Please only select side and drink type for non-regular size"
            elif size == "regular":
                self._outputs['size'] = size

        # process serving size quantity unit:
        size = form.get("unit", None)
        allowableUnit = ["unit", "g", "ml"]
        if size not in allowableUnit:
            self._other_errors['unit'] = "Please enter valid unit"
        elif actualType:
            if size != "unit":
                if smlSize != True:
                    self._other_errors['unit'] = "If choosing regular serving size, must choose regular unit"
                else:
                    allowableType = [IngredientType.SIDE, IngredientType.DRINK]
                    if actualType not in allowableType:
                        self._other_errors['unit'] = "Must be stored as regular unit if ingredient is not side or drink"
                    elif size == "ml" and actualType != IngredientType.DRINK:
                        self._other_errors['unit'] = "Must be type drink to be stored in ml"
                    elif size == "g" and actualType == IngredientType.DRINK:
                        self._other_errors['unit'] = "Drink can not be stored in grams"
                    else:
                        self._outputs['unit'] = size
            else:
                self._outputs['unit'] = size

        # process serving size quantities
        # small, medium, large size quantity
        sQty = form.get("sQty", None)
        mQty = form.get("mQty", None)
        lQty = form.get("lQty", None)
        if smlSize == False and all([sQty != "", mQty != "", lQty != ""]):
            self._other_errors['qty'] = "Please enter serving size quantity only if choosing non-regular size"
        elif smlSize == True:
            if any([sQty == "", mQty == "", lQty == ""]):
                self._other_errors['qty'] = "Please enter serving quantity for all three serving sizes"
            else:
                quantities = {"small size":sQty, "medium size":mQty, "large size":lQty}
                validQty = True
                for name, q in quantities.items():
                    try:
                        q = int(q)
                    except ValueError:
                        self._other_errors[name] = "Please enter integer quantity for " + name
                        validQty = False
                if quantities["small size"] >= quantities["medium size"] or quantities["medium size"] >= quantities["large size"]:
                    self._other_errors["varySize"] = "Please enter varying ordered quantities for the three sizes"
                    validQty = False
                if validQty == True:
                    self._outputs['sQty'] = int(sQty)
                    self._outputs['mQty'] = int(mQty)
                    self._outputs['lQty'] = int(lQty)

    @property
    def outputs(self):
        return self._outputs

class SideDrinkForm(Form):

    def __init__(self, form):
        self._fields = []
        # Errors not specific to a single field
        self._other_errors = {}
        self._outputs = {}
        for name, quantity in form.items():
             if name.find("_size") == -1:
                if quantity != '' and quantity != '0':
                    tmp = Field(name, [PositiveInput(name), 
                            SufficientStock(name, form.get(str(name)+"_size", None))])
                    try:
                        self._outputs[name] = [form.get(str(name)+"_size"), int(quantity)]
                    except ValueError:
                        self._other_errors[name] = "Please enter integer quantity for " + str(name)
                    else:
                        self._fields.append(tmp)
        self._parse(form)

    @property
    def outputs(self):
        return self._outputs

    def _parse(self, form):
        ingredients = {}
        for field in self._fields:
            field.parse(form.get(field.name))


'''
FIELDS
'''
class Field():
    def __init__(self, name, validators = None):
        self._name = name
        self._validators = validators or []
        self._error     = None
        self._raw_data  = None
        self._data      = None

    def parse(self, raw_data):
        '''
        raw_data: user input for the field
        '''
        self._raw_data = raw_data
        try:
            # validate form 
            for v in self._validators:  
                v.validate(raw_data)
            
            # transform raw_data (of type string) into the desired data type or format
            self._transform(raw_data)   

        except ParseError as pe:
            self._error = str(pe)



    def _transform(self, raw_data):
        self._data = raw_data # apply no transform for basic fields

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    @property
    def error(self):
        return self._error

    @property
    def raw_data(self):
        return self._raw_data
    
    @property
    def is_valid(self):
        return self._error is None



'''
FORM VALIDATORS
'''
class Validator(ABC):

    def __init__(self, name, error_msg=''):
        self._name = name
        self._error_msg = error_msg

    @abstractmethod
    def validate(self, raw_data):
        pass


class PositiveInput(Validator):

    def __init__(self, name):
        return super().__init__(name, name.capitalize() + ' cannot be negative')

    def validate(self, raw_data):
        try:
            if int(raw_data) < 0:
                raise ParseError(self._error_msg)
        except ValueError:
            raise ParseError("Please enter integer input for " + self._name)

class SufficientStock(Validator):

    def __init__(self, name, size="regular"):
        self._error_msg = 'Insufficient stock for ' + name.capitalize()
        self._name = name
        self._size = size
    
    def validate(self, raw_data):
        try:
            val = int(raw_data)
        except ValueError:
            raise ParseError("Please enter integer quantity for " + self._name)
        else:
            try:
                ingredient = system.inventory.getIngredient(self._name)
            except InventoryError as ie:
                raise ParseError(ie.msg)
            if self._size == None:
                raise ParseError("Please select size for " + name)
            elif self._size not in ingredient.servingSizes:
                raise ParseError("Please select valid size for " + name)
            if system.inventory.checkSufficientStock(self._name, val, self._size) == False:
                raise ParseError(self._error_msg)

class MaintainStock(Validator):
    def __init__(self, name, error_msg='This ingredient has insufficient stock'):
        self._error_msg = error_msg
        self._name = name
    
    def validate(self, raw_data):
        try:
            val = int(raw_data)
        except ValueError:
            raise ParseError("Please enter integer input for " + self._name)
        else:
            ingredient = system.inventory.getIngredient(self._name)
            if val + ingredient.quantity < 0:
                raise ParseError(self._error_msg)