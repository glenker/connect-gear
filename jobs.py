
from gear_handler import gear_handler

class jobs(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self):
        return {'a':'b', 'c':'d'}

