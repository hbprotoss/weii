#coding=utf-8

import configparser
import json

from PyQt4.QtGui import *

class ConfParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr
    
class Account:
    def __init__(self, plugin, avater_manager, emotion_manager, picture_manager):
        # Plugin object
        self.plugin = plugin
        
        # QPixmap object
        self.service_icon = QPixmap(self.plugin.service_icon)
        
        # Resource manager
        self.emotion_manager = emotion_manager
        self.avater_manager = avater_manager
        self.picture_manager = picture_manager
        
        try:
            self.emotion_list = json.load(open(emotion_manager.path+'/emotion.json'))
        except IOError:
            self.emotion_list = self.plugin.getEmotions()
            json.dump(self.emotion_list, open(emotion_manager.path+'/emotion.json', 'w'))