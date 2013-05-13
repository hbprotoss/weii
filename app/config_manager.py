# coding=utf-8

import json
import atexit

from app import constant
from app import misc

SECTION = 'Global Config'
PROXY = 'Proxy'

parser = misc.ConfParser()

def initConfig():
    initValue()
    parser.read(constant.GLOBAL_CONFIG)
    
    # New configuration
#    if not parser.has_section(SECTION):
#        parser.add_section(SECTION)
#        parser.set(SECTION, 'Proxy', json.dumps({}))
        
    # Write back at exit
    atexit.register(onExit)
        
def initValue():
    parser[SECTION] = {}
    parser[SECTION][PROXY] = json.dumps({})
    
def onExit():
    parser.write(open(constant.GLOBAL_CONFIG, 'w'))

initConfig()
    
########################################################
# Exports
def getParameter(key):
    return parser.get(SECTION, key)

def setParameter(key, value):
    parser.set(SECTION, key, value)
