# coding=utf-8

import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app.widget.ContentWidget import abstract_widget
from app import logger
from app import database_manager

log = logger.getLogger(__name__)

class AtWidget(abstract_widget.AbstractTweetContainer):
    def __init__(self, parent=None):
        super(AtWidget, self).__init__('Mention', parent)
    
    def retrieveData(self, account_list, page=1, count=20):
        rtn = []
        for account in account_list:
            try:
                log.info(account.plugin)
                tweet_list = account.plugin.getMentionTimeline(max_point=(account.last_tweet_id, account.last_tweet_time),
                    page=page, count=count
                )
                for tweet in tweet_list:
                    tweet['type'] = abstract_widget.TWEET
                rtn.append((account, tweet_list))
                database_manager.insertHistory('Mention',
                    [json.dumps(tweet) for tweet in tweet_list],
                    account.plugin.service,
                    account.plugin.uid
                )
            except Exception as e:
                rtn.append((account, {'error': str(e)}))
            
        log.info('Download finished')
        return (rtn, )
