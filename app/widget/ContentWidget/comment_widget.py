# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import logger
from app.widget.ContentWidget import abstract_widget

log = logger.getLogger(__name__)

class CommentWidget(abstract_widget.AbstractTweetContainer):
    def retrieveData(self, account_list, page=1, count=20):
        rtn = []
        for account in account_list:
            log.debug(account.plugin)
            tweet_list = account.plugin.getComment(max_point=(account.last_tweet_id, account.last_tweet_time),
                page=page, count=count
            )
            for tweet in tweet_list:
                tweet['reposts_count'] = 0
                tweet['comments_count'] = 0
                tweet['retweeted_status'] = tweet['status']
                del tweet['status']
            rtn.append((account, tweet_list))
            
        log.debug('Download finished')
        return (rtn, ), {}