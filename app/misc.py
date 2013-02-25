#coding=utf-8

import configparser

class ConfParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr
    
class Account:
    # Plugin object
    plugin = None
    
    # QPixmap object
    service_icon = None