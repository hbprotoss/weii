# coding=utf-8

import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import logger
from app import database_manager
from app.widget.ContentWidget import abstract_widget

log = logger.getLogger(__name__)

class CommentWidget(abstract_widget.AbstractTweetContainer):
    # FIXME: TweetWidget too loose when there is only one tweet
    def __init__(self, parent=None):
        super(CommentWidget, self).__init__('Comment', parent)
    
    def retrieveData(self, account_list, page=1, count=20):
        rtn = []
        for account in account_list:
            try:
                log.info(account.plugin)
                tweet_list = account.plugin.getCommentTimeline(max_point=(account.last_tweet_id, account.last_tweet_time),
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
    #                else:
    #                    tweet['retweeted_status'] = tweet['status']
                rtn.append((account, tweet_list))
                database_manager.insertHistory('Comment',
                    [json.dumps(tweet) for tweet in tweet_list],
                    account.plugin.service,
                    account.plugin.uid
                )
            except Exception as e:
                rtn.append((account, {'error': str(e)}))
            
        log.info('Download finished')
        return (rtn, )
