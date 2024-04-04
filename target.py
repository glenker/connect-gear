import os
from flask import request
import json
from gear_handler import gear_handler
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
class targets(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self):
        data = []
        if request.method == "POST":
            if "target" in request.form.keys():
                target = request.form["target"]
                logger.info("[+] setting target to "+target)

        for _, dirnames, filenames in os.walk('targets'):
            for target in dirnames:
                data.append({"name":target, "children": [
                    {"name": "view", "click":"javascript:void(0)"},
                    {"name": "config", "click":"javascript:void(0)"},
                    {"name": "testcase", "click":"javascript:void(0)"},
                    {"name": "upload", "click":"javascript:void(0)"},
                    {"name": "coverage", "click":"javascript:void(0)"},
                    {"name": "stats", "click":"javascript:void(0)"}
                ]})
            break

        data = {"name":"root", "children":data,
                "console":['one two three']}
        return json.dumps(self.expand_hierarchy(data))