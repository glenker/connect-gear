#!/usr/bin/env python3
from capstone import *
from gear_handler import gear_handler
from flask import request

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
class cude():
    def __init__(self, code):
        self.code = code
    
def cappy_code():
    CODE = b"\x55\x48\x8b\x05\xb8\x13\x00\x00"
    CODE+= b"\xf1\x02\x03\x0e\x00\x00\xa0\xe3\x02\x30\xc1\xe7\x00\x00\x53\xe3"

    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for i in md.disasm(CODE, 2):
        yield ("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
    

    
class view(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self, project):
        return {"name": "root", "children": [{"name": project}]}

class stats(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self, project):
        return {"name": "root", "children": [{"name": "test"}]}

class config(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self, project):
        return {"name": "root", "children": [{"name": "test"}]}

class upload(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self, project):
        return {"name": "root", "children": [{"name": "test"}]}


class testcase(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self, project):
        return {"name": "root", "children": [{"name": "test"}]}

class coverage(gear_handler):
    def __init__(self):
        super().__init__()

    def dispatch_request(self, project):
        return {"name": "root", "children": [{"name": "test"}]}

if __name__ == '__main__':
    print (cappy_code())