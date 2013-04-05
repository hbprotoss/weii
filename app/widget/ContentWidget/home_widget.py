# coding=utf-8

import json
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from widget.ContentWidget import abstract_widget
from widget.tweet_widget import TweetWidget
from app import logger
from app import account_manager
from app import dateutil
from app import easy_thread
from app.dateutil import parser

log = logger.getLogger(__name__)
SIGNAL_FINISH = 'downloadFinish'

class TweetData():
    def __init__(self, account, tweet_list, picture_list):
        self.account = account
        self.tweet_list = tweet_list
        self.picture_list = picture_list

class HomeWidget(abstract_widget.AbstractWidget):
    '''
    Home tab
    '''
    
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__(parent)
        self.currentPage = 1
        self.time_format = '%a %b %d %H:%M:%S %z %Y'
        self.refreshing = False
        
        # debug
        #self.tweets = (tweet for tweet in json.load(open('json'))['statuses'])
        
    def updateUI(self, data):
        log.debug('updateUI')
        self.clearWidget(self.refreshing_image)
        whole_list = []
        for account,tweet_list in data:
            # If it is refreshing, update max_point of account
            if self.count() == 1:
                account.last_tweet_id = tweet_list[0]['id']
                account.last_tweet_time = tweet_list[0]['created_at']
                
            for tweet in tweet_list:
                dt = parser.parse(tweet['created_at'])
                res = dt.astimezone(dateutil.tz.tzlocal())
                tweet['created_at'] = time.mktime(res.timetuple())
                
                if 'retweeted_status' in tweet:
                    retweet = tweet['retweeted_status']
                    dt = parser.parse(retweet['created_at'])
                    res = dt.astimezone(dateutil.tz.tzlocal())
                    retweet['created_at'] = time.mktime(res.timetuple())
                whole_list.append((account, tweet))
        
        whole_list.sort(key=lambda x:x[1]['created_at'], reverse=True)
                
        for account, tweet in whole_list:
            avatar = self.small_loading_image
            picture = self.loading_image
                
            self.addWidget(
                TweetWidget(account, tweet, avatar, picture, self)
            )
        self.refreshing = False
        
    def retrieveTweets(self, account_list, page=1, count=20):
        self.refreshing = True
        rtn = []
        for account in account_list:
            log.debug(account.plugin)
            tweet_list = account.plugin.getTimeline(max_point=(account.last_tweet_id, account.last_tweet_time),
                page=page, count=count
            )
            rtn.append((account, tweet_list))
            
        log.debug('Download finished')
        return (rtn, ), {}
        
    def appendNew(self):
        # FIXME: Possibal duplicate tweet when turn to next page
        if self.refreshing:
            return
        
        account_list = account_manager.getCurrentAccount()
        
        self.refreshing_image.show()
        self.insertWidget(-1, self.refreshing_image)
        
        easy_thread.start(self.retrieveTweets, args=(account_list, self.currentPage, 20), callback=self.updateUI)
        log.debug('Starting thread')
        self.currentPage += 1
        
    def refresh(self):
        if self.refreshing:
            return
        
        account_list = account_manager.getCurrentAccount()
        
        for account in account_list:
            account.last_tweet_id = 0
            account.last_tweet_time = 0
            
        self.clearAllWidgets()
        self.refreshing_image.show()
        self.insertWidget(0, self.refreshing_image)
        
        easy_thread.start(self.retrieveTweets, args=(account_list, 1, 20), callback=self.updateUI)
        log.debug('Starting thread')
        self.currentPage = 2
        
#    def refresh(self):
#        '''
#        For debug purpose
#        '''
#        account_list = account_manager.getCurrentAccount()
#        account_list[0].last_tweet_id = account_list[0].last_tweet_time = 0
#        self.clearAllWidgets()
#        tweets = json.load(open('json'))['statuses']
#        self.updateUI([(account_list[0], tweets)])
