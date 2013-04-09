# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app.widget.ContentWidget import abstract_widget
from app import logger

log = logger.getLogger(__name__)

class AtWidget(abstract_widget.AbstractTweetContainer):
    def retrieveData(self, account_list, page=1, count=20):
        rtn = []
        for account in account_list:
            log.debug(account.plugin)
            tweet_list = account.plugin.getMentions(max_point=(account.last_tweet_id, account.last_tweet_time),
                page=page, count=count
            )
            rtn.append((account, tweet_list))
            
        log.debug('Download finished')
        return (rtn, ), {}