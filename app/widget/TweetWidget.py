#coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ContentWidget(QWidget):
    '''
    Widget for each tweet
    '''
    
    def __init__(self, parent, tweet, service_icon, avater, pictures):
        super(ContentWidget, self).__init__(parent)
        '''
        @param tweet: dict of tweet. See doc/插件接口设计.pdf: 单条微博
        @param service_icon: QPixmap containing service icon
        @param avater: QPixmap of user avater
        @param pictures: list of QPixmap, including small, middle and original picture
        @return: None
        '''
        
        self.tweet = tweet
        self.service_icon = service_icon
        self.avater = avater
        self.pictures = pictures
        
        hLayout = QHBoxLayout()
        self.setLayout(hLayout)
        
        # avater
        v1 = QVBoxLayout()
        hLayout.addLayout(v1)
        label_avater = QLabel()
        label_avater.setPixmap(self.avater)
        v1.addWidget(label_avater)
        v1.addStretch()
        
        # tweet
        v2 = QVBoxLayout()
        hLayout.addLayout(v2)
        
        ## user, source, service
        h1 = QHBoxLayout()
        v2.addLayout(h1)
        label_user = QLabel(self.tweet['user']['screen_name'])
        label_source = QLabel(self.tweet['source'])
        label_service_icon = QLabel()
        label_service_icon.setPixmap(self.service_icon)
        h1.addWidget(label_user)
        h1.addWidget(label_source)
        h1.addStretch()
        h1.addWidget(label_service_icon)
        
        ## tweet content
        label_tweet = QLabel(self.tweet['text'])
        v2.addWidget(label_tweet)
        
        ## retweet if exists
        if(tweet.has_key('retweet_status')):
            retweet = tweet['retweet_status']
            
            groupbox = QGroupBox()
            v2.addLayout(groupbox)
            v3 = QVBoxLayout()
            groupbox.setLayout(v3)
            
            h3 = QHBoxLayout()
            v3.addLayout(h3)
            label_retweet_user = QLabel(retweet['user']['screen_name'])
            label_retweet_source = QLabel(retweet['source'])
            h3.addWidget(label_retweet_user)
            
            label_retweet = QLabel(retweet['text'])
            v3.addWidget(label_retweet)
            
            if(self.pictures):
                v3.addWidget(self.pictures[0])
                
            h4 = QHBoxLayout()
            v3.addLayout(h4)
            label_retweet_time = QLabel(retweet['create_at'])
            label_retweet_repost = QLabel('转发(%s)' % str(retweet['reposts_count']))
            label_retweet_comment = QLabel('评论(%s)' % str(retweet['comments_count']))
            h4.addWidget(label_retweet_time)
            h4.addStretch()
            h4.addWidget(label_retweet_repost)
            h4.addWidget(label_retweet_comment)
        ## No retweet and has picture
        elif(self.pictures):
            v2.addWidget(self.pictures[0])
        
        v2.addStretch()
        
        ## time, repost, comment
        h2 = QHBoxLayout()
        v3.addLayout(h2)
        label_tweet_time = QLabel(tweet['create_at'])
        label_tweet_repost = QLabel('转发(%s)' % str(tweet['reposts_count']))
        label_tweet_comment = QLabel('评论(%s)' % str(tweet['comments_count']))
        h2.addWidget(label_tweet_time)
        h2.addStretch()
        h2.addWidget(label_tweet_repost)
        h2.addWidget(label_tweet_comment)