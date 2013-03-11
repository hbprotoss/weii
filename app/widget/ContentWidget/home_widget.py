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
        self.page = 1
        self.count = 20
        
    def setAccountList(self, account_list):
        self.account_list = account_list
    
    def setParams(self, page=1, count=20):
        self.page = page
        self.count = count
        
    def run(self):
        rtn = []
        for account in self.account_list:
            tweet_list = account.plugin.getTimeline(max_point=(account.last_tweet_id, account.last_tweet_time),
                page=self.page, count=self.count
            )
            rtn.append((account, tweet_list))
            
        log.debug('Download finished')
        self.emit(SIGNAL(SIGNAL_FINISH), rtn)

class HomeWidget(abstract_widget.AbstractWidget):
    '''
    Home tab
    '''
    
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent)
        self.download_task = DownloadTask()
        self.currentPage = 1
        
        self.connect(self.download_task, SIGNAL(SIGNAL_FINISH), self.updateUI)
        
        # debug
        #self.tweets = (tweet for tweet in json.load(open('json'))['statuses'])
        
    def updateUI(self, data):
        log.debug('updateUI')
        self.clearWidget(self.refreshing_image)
        for account,tweet_list in data:
            # If it is refreshing, update max_point of account
            if self.count() == 1:
                account.last_tweet_id = tweet_list[0]['id']
                account.last_tweet_time = tweet_list[0]['created_at']
                
            for tweet in tweet_list:
                avatar = self.small_loading_image
                picture = self.loading_image
                    
                self.addWidget(
                    TweetWidget(account, tweet, avatar, picture, self)
                )
        
    def appendNew(self, account_list):
        if not self.download_task.isRunning():
            self.refreshing_image.show()
            self.insertWidget(-1, self.refreshing_image)
            
            self.download_task.setParams(self.currentPage)
            self.currentPage += 1
            self.download_task.setAccountList(account_list)
            log.debug('Starting thread')
            self.download_task.start()
        
    def refresh(self, account_list):
        if not self.download_task.isRunning():
            for account in account_list:
                account.last_tweet_id = 0
                account.last_tweet_time = 0
                
            self.clearAllWidgets()
            self.refreshing_image.show()
            self.insertWidget(0, self.refreshing_image)
            
            self.download_task.setParams(1)
            self.currentPage = 2
            self.download_task.setAccountList(account_list)
            log.debug('Starting thread')
            self.download_task.start()
            
#    def refresh(self, account_list):
#        account_list[0].last_tweet_id = account_list[0].last_tweet_time = 0
#        self.clearAllWidgets()
#        tweets = json.load(open('json'))['statuses']
#        for tweet in tweets:
#            widget = TweetWidget(account_list[0], tweet, self.small_loading_image, self.loading_image, self)
#            self.addWidget(widget)
#        pass
    
#    def refresh(self, account_list):
#        self.addWidget(TweetWidget(None, next(self.tweets), self.avatar.scaled(constant.AVATER_IN_TWEET_SIZE, constant.AVATER_IN_TWEET_SIZE), None, self))
