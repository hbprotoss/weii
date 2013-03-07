# coding=utf-8

import json
import imghdr
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from widget.ContentWidget import abstract_widget
from widget.tweet_widget import TweetWidget
from app import constant
from app import logger

log = logger.getLogger(__name__)
SIGNAL_FINISH = 'downloadFinish'

class TweetData():
    def __init__(self, account, tweet_list, picture_list):
        self.account = account
        self.tweet_list = tweet_list
        self.picture_list = picture_list

class DownloadTask(QThread):
    def __init__(self):
        #super(DownloadTask, self).__init__(self)
        QThread.__init__(self)
        
    def setAccountList(self, account_list):
        self.account_list = account_list
        
    def run(self):
        rtn = []
        for account in self.account_list:
            tweet_list = account.plugin.getTimeline()
            rtn.append((account, tweet_list))
            
        log.debug('Download finished')
        self.emit(SIGNAL(SIGNAL_FINISH), rtn)

class HomeWidget(abstract_widget.AbstractWidget):
    '''
    Home tab
    '''
    
    def __init__(self, theme, parent=None):
        super(HomeWidget, self).__init__(theme, parent)
        self.download_task = DownloadTask()
        self.loading_image = QMovie(theme.skin['loading-image'])
        self.loading_image.start()
        
        self.small_loading_image = QMovie(theme.skin['loading-image'])
        self.small_loading_image.setScaledSize(QSize(constant.AVATER_IN_TWEET_SIZE, constant.AVATER_IN_TWEET_SIZE))
        self.small_loading_image.start()
        
        self.connect(self.download_task, SIGNAL(SIGNAL_FINISH), self.updateUI)
        
        # debug
        self.tweets = (tweet for tweet in json.load(open('json'))['statuses']) 
        
    def updateUI(self, data):
        log.debug('updateUI')
        for account,tweet_list in data:
            for tweet in tweet_list:
                avatar = self.small_loading_image
                picture = self.loading_image
                    
                self.addWidget(
                    TweetWidget(account, tweet, avatar, picture, self)
                )
        
#    def refresh(self, account_list):
#        if not self.download_task.isRunning():
#            self.download_task.setAccountList(account_list)
#            log.debug('Starting thread')
#            self.download_task.start()
            
    def refresh(self, account_list):
        self.clearWidget()
        tweets = json.load(open('json'))['statuses']
        for tweet in tweets:
            widget = TweetWidget(account_list[0], tweet, self.small_loading_image, self.loading_image, self)
            self.addWidget(widget)
        pass
    
#    def refresh(self, account_list):
#        self.addWidget(TweetWidget(None, next(self.tweets), self.avatar.scaled(constant.AVATER_IN_TWEET_SIZE, constant.AVATER_IN_TWEET_SIZE), None, self))
