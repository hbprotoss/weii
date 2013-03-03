#coding=utf-8

import logging

def getLogger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    #ch.terminator = ''
    formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
    ch.setFormatter(formatter)
    
    log.addHandler(ch)
    
    return log