#coding=utf-8

import logging

g_level = None

def getLogger(name):
    log = logging.getLogger(name)
    log.setLevel(g_level)
    
    formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
    
    # Standard output handler
    sh = logging.StreamHandler()
    sh.setLevel(g_level)
    sh.setFormatter(formatter)
    log.addHandler(sh)
    
    # File output handler
    fh = logging.FileHandler('weii.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    log.addHandler(fh)
    
    return log

def setLogLevel(level):
    global g_level
    g_level = getattr(logging, level.upper())