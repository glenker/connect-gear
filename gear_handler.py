
from flask import render_template
from flask.views import View

class gear_handler(View):
    def __init__(self):
        super().__init__()

    def dispatch_request(self):
        return render_template('viewer.html')

    def expand_hierarchy(self, d):
        if "children" in d.keys():
            d["children"] = [self.expand_hierarchy(e) for e in d["children"]]
        elif "value" not in d.keys():
            d["value"] = 1
        return d