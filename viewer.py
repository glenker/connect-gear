
from flask import render_template
from gear_handler import gear_handler

class viewer(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self):
        return render_template('viewer.html')