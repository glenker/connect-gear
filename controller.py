#!/usr/bin/env python3

import os, sys

#from capstone import *
from viewer import viewer
from network import network
from jobs import jobs
from target import targets
from code import view, stats, config, upload, testcase, coverage
from gear_handler import gear_handler

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from flask import Flask, send_from_directory
app = Flask(__name__, static_folder='static')

def expand_hierarchy(d):
    if "children" in d.keys():
        d["children"] = [expand_hierarchy(e) for e in d["children"]]
    elif "value" not in d.keys():
        d["value"] = 1
    return d

@app.route("/static/<path:static_file>")
def static_route(static_file):
    if static_file not in ['style.css/', 'inconsolata.ttf/', 'favicon.ico']:
        logging.info("invalid static request "+static_file)
        return ""
    else:
        return (send_from_directory(os.path.join(app.root_path, 'static'), static_file))

@app.route("/js/<path:js_file>")
def js_handler(js_file):
    javascript_list = ['d3.v5.js', 'd3.v5.min.js', 'core.js', 'proto.js']
    if js_file not in javascript_list:
        logging.critical("invalid JS request "+js_file)
        return ("invalid JS request "+js_file)
    else:
        try:
            os.stat(js_file)
            ofp = open(js_file, "r")
            lines = ofp.readlines()
            ofp.close()
            return ("".join(lines))
        except FileNotFoundError as err:
            logger.critical("File \""+js_file+"\" not found\n")
            return ("File \""+js_file+"\" not found\n")
        except Exception as e:
            logger.critical("JS handler exception "+str(e)+"\n")
            return ("JS handler exception "+str(e)+"\n")

handlers = [('/', viewer),
            ('/index.html', viewer),
            ('/network', network()),
            ('/jobs', jobs()),
            ('/targets', targets()),
            ('/view/<project>', view()),
            ('/stats/<project>', stats()),
            ('/config/<project>', config()),
            ('/upload/<project>', upload()),
            ('/testcase/<project>', testcase()),
            ('/coverage/<project>', coverage())]
for route, handler in handlers:
    app.add_url_rule(route, view_func=handler.as_view(route))

app.run()


