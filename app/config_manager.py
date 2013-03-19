# coding=utf-8

from app import constant
from app import misc

SECTION = 'Global Config'

conf = {}

def initConfig():
    parser = misc.ConfParser()
    parser.read(constant.GLOBAL_CONFIG)
    
    conf.update(parser.items(SECTION))

initConfig()
    
########################################################
# Exports
def getParameter(key):
    return conf[key]

def setParameter(key, value):
    conf[key] = value