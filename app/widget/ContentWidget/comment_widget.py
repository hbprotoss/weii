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
                tweet['type'] = abstract_widget.COMMENT
                tweet['reposts_count'] = 0
                tweet['comments_count'] = 0
                # Show comment if this tweet is a comment of another, or original tweet otherwise.
                if 'reply_comment' in tweet:
                    tweet['retweeted_status'] = tweet['reply_comment']
                    reply = tweet['reply_comment']
                    reply['reposts_count'] = 0
                    reply['comments_count'] = 0
                else:
                    tweet['retweeted_status'] = tweet['status']
            rtn.append((account, tweet_list))
            
        log.debug('Download finished')
        return (rtn, ), {}