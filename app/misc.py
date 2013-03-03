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
    
    # Resource manager
    emotion_manager = None
    avater_manager = None
    picture_manager = None