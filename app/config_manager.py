# coding=utf-8

import json

from app import constant
from app import misc

SECTION = 'Global Config'

parser = misc.ConfParser()

def initConfig():
    parser.read(constant.GLOBAL_CONFIG)
    
    # New configuration
    if not parser.has_section(SECTION):
        parser.add_section(SECTION)
        parser.set(SECTION, 'Proxy', json.dumps({}))

initConfig()
    
########################################################
# Exports
def getParameter(key):
    return parser.get(SECTION, key)

def setParameter(key, value):
    parser.set(SECTION, key, value)
    parser.write(open(constant.GLOBAL_CONFIG, 'w'))