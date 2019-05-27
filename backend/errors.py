class InventoryError(Exception):
    def __init__(self, msg):
        self._msg = msg
    @property
    def msg(self):
        return self._msg 

class OrderError(Exception):
    def __init__(self, msg):
        self._msg = msg

    @property
    def msg(self):
        return self._msg

class SystemError(Exception):
    def __init__(self, msg):
        self._msg = msg

    @property
    def msg(self):
        return self._msg