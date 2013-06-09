#coding=utf-8

import logging

g_level = None
with open('weii.log', 'a+') as f:
    f.write('#'*80)
    f.write('\n')

def getLogger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    
    # Standard output handler
    sh = logging.StreamHandler()
    sh.setLevel(g_level)
    sh.setFormatter(logging.Formatter('%(levelname)s - %(name)s:%(lineno)s: %(message)s'))
    log.addHandler(sh)
    
    # File output handler
    fh = logging.FileHandler('weii.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s:%(lineno)s: %(message)s'))
    log.addHandler(fh)
    
    return log

def setLogLevel(level):
    global g_level
    g_level = getattr(logging, level.upper())