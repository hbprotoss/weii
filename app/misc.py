#coding=utf-8

import configparser
import json
from collections import namedtuple

from PyQt4.QtGui import *

EmotionExp = namedtuple('EmotionExp', ['prefix', 'suffix'])

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
        
        # emotion_list contains category information. Used when posting tweet
        try:
            self.emotion_list = json.load(open(emotion_manager.path+'/emotion.json'))
        except IOError:
            self.emotion_list = self.plugin.getEmotions()
            json.dump(self.emotion_list, open(emotion_manager.path+'/emotion.json', 'w'))
            
        # emotion_dict contains name to url mapping
        self.emotion_dict = self.getEmotionDict(self.emotion_list)
            
        self.emotion_exp = EmotionExp._make(self.plugin.getEmotionExpression())
        pass
        
    def getEmotionDict(self, emotion_list):
        rtn = {}
        for category in emotion_list.keys():
            for emotion in emotion_list[category]:
                rtn[emotion['name']] = emotion['url']
                
        return rtn