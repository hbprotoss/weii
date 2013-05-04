# coding=utf-8

'''
Module for junk ads filtering based on keywords.
Need upgrades if performance problem appears in the future.
'''

from app import constant

try:
    file = open(constant.KEYWORDS_FILE)
except IOError:
    file = open(constant.KEYWORDS_FILE, 'x')
    file.close()
    file = open(constant.KEYWORDS_FILE)
keywords = [keyword.rstrip('\n') for keyword in file if len(keyword) > 1]

def checkForJunk(src):
    for keyword in keywords:
        if keyword in src:
            return True
    return False