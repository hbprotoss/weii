# coding=utf-8

import time
import random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from widget.ContentWidget import AbstractWidget
from widget.TweetWidget import TweetWidget
from app import constant


class HomeWidget(AbstractWidget.AbstractWidget):
    '''
    Home tab
    '''
    
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent)
        self.service_icon = QPixmap(constant.TEST_SERVICE)
        self.avater = QPixmap(constant.DEFAULT_AVATER)
        
    def refresh(self, account_list):
        #self.insertWidget(0, QLabel('Homewidget ' + time.asctime()))
        for i in range(10):
            tweet = {
                'user': {'screen_name': 'dummy'},
                'source': 'source',
                'text': 'tweet ' + str(i),
                'create_at': '1989-6-4',
                'reposts_count': 0,
                'comments_count': 0
            }
            if(random.randrange(0, 2)):
                tweet['retweet_status'] = {
                    'user': {'screen_name': 'dummy'},
                    'source': 'source',
                    'text': 'retweet ' + str(i),
                    'create_at': '1989-6-4',
                    'reposts_count': 0,
                    'comments_count': 0
                }
            self.insertWidget(0, TweetWidget(None, tweet, self.service_icon, self.avater.scaled(40, 40), None))
            #self.insertWidget(0, QLabel(str(i)))
        pass