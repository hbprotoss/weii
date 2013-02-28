# coding=utf-8

import time
import random
import json
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from widget.ContentWidget import abstract_widget
from widget.tweet_widget import TweetWidget
from app import constant


class HomeWidget(abstract_widget.AbstractWidget):
    '''
    Home tab
    '''
    
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent)
        self.service_icon = QPixmap(constant.TEST_SERVICE)
        self.avater = QPixmap(constant.DEFAULT_AVATER)
        
        # debug
        self.tweets = (tweet for tweet in json.load(open('json'))['statuses']) 
        
#    def refresh(self, account_list):
#        for account in account_list:
#            timeline = account.plugin.getTimeline()
#            for tweet in timeline:
#                self.addWidget(TweetWidget(
#                    account, tweet, account.service_icon, self.avater.scaled(40, 40), None, self))
            
    def refresh(self, account_list):
        tweets = json.load(open('json'))['statuses']
        for tweet in tweets:
            widget = TweetWidget(None, tweet, self.service_icon, self.avater.scaled(40, 40), None, self)
            self.addWidget(widget)
            #self.insertWidget(0, QLabel(str(i)))
        pass
    
#    def refresh(self, account_list):
#        self.addWidget(TweetWidget(None, next(self.tweets), self.service_icon, self.avater.scaled(40, 40), None, self))
