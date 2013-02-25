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
        for account in account_list:
            timeline = account.plugin.getTimeline()
            for tweet in timeline:
                self.addWidget(TweetWidget(
                    account, tweet, account.service_icon, self.avater.scaled(40, 40), None))
            
#    def refresh(self, account_list):
#        #self.insertWidget(0, QLabel('Homewidget ' + time.asctime()))
#        for i in range(10):
#            tweet = {
#                'user': {'screen_name': '网络安全俱乐部'},
#                'source': 'source',
#                'text': '转发微博',
#                'created_at': '1989-06-04 00:00:00',
#                'reposts_count': 0,
#                'comments_count': 0
#            }
#            if(random.randrange(0, 2)):
#                tweet['retweeted_status'] = {
#                    'user': {'screen_name': 'FreebuF黑客与极客'},
#                    'source': 'source',
#                    'text': '【树莓派（Raspberry Pi）渗透测试系统—PwnPi v3.0发布】PwnPi是为树莓派（Raspberry Pi）开发的渗透测试发行版。它基于Linux操作系统，最新的3.0版本预装了超过200个网络安全工具可以很好的帮助渗透测试人员进相关工作。详情点击http://t.cn/zY0nbxs',
#                    'created_at': '1989-06-04 00:00:00',
#                    'reposts_count': 0,
#                    'comments_count': 0
#                }
#            self.addWidget(TweetWidget(None, tweet, self.service_icon, self.avater.scaled(40, 40), None))
#            #self.insertWidget(0, QLabel(str(i)))
#        pass