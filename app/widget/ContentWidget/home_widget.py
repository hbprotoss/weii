# coding=utf-8

import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app.widget.ContentWidget import abstract_widget
from app import database_manager
from app import logger

log = logger.getLogger(__name__)

class TweetData():
    def __init__(self, account, tweet_list, picture_list):
        self.account = account
        self.tweet_list = tweet_list
        self.picture_list = picture_list

class HomeWidget(abstract_widget.AbstractTweetContainer):
    '''
    Home tab
    '''
    def __init__(self, parent=None):
        super(HomeWidget, self).__init__('Timeline', parent)
    
    def retrieveData(self, account_list, page=1, count=20):
        rtn = []
        for account in account_list:
            #log.debug(account.plugin)
            try:
                tweet_list = account.plugin.getTimeline(max_point=(account.last_tweet_id, account.last_tweet_time),
                    page=page, count=count
                )
                for tweet in tweet_list:
                    tweet['type'] = abstract_widget.TWEET
                rtn.append((account, tweet_list))
                database_manager.insertHistory('Timeline',
                    [json.dumps(tweet) for tweet in tweet_list],
                    account.plugin.service,
                    account.plugin.uid
                )
            except Exception as e:
                rtn.append((account, {'error': str(e)}))
            
        log.debug('Download finished')
        return (rtn, )
