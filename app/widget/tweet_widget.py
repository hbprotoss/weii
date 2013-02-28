#coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import analyse_tweet

class Text(QLabel):
    def __init__(self, text, parent=None):
        rich_text = analyse_tweet.analyse(text)
        super(Text, self).__init__(rich_text, parent)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse)
        
class TweetText(Text):
    def __init__(self, text, parent=None):
        super(TweetText, self).__init__(text, parent)
        self.setWordWrap(True)

class TweetWidget(QWidget):
    '''
    Widget for each tweet
    '''
    
    def __init__(self, account, tweet, avater, thumbnail, parent=None):
        '''
        @param account: misc.Account object
        @param tweet: dict of tweet. See doc/插件接口设计.pdf: 单条微博
        @param avater: QPixmap of user avater
        @param thumbnail: QPixmap of thumbnail related to tweet
        @return: None
        '''
        super(TweetWidget, self).__init__(parent)
        
        self.account = account
        self.tweet = tweet
        self.avater = avater
        self.thumbnail = thumbnail
        
        self.setupUI()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding))
        
    def renderUI(self, theme):
        '''
        @param theme: Theme.Theme object
        @return: None
        '''
        
    def setupUI(self):
        hLayout = QHBoxLayout()
        hLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(hLayout)
        
        # avater
        v1 = QVBoxLayout()
        hLayout.addLayout(v1)
        label_avater = QLabel(self)
        label_avater.setPixmap(self.avater)
        v1.addWidget(label_avater)
        v1.addStretch()
        
        # tweet
        v2 = QVBoxLayout()
        hLayout.addLayout(v2)
        
        ## user, source, service
        h1 = QHBoxLayout()
        v2.addLayout(h1)
        label_user = Text('@' + str(self.tweet['user']['screen_name']), self)
        #label_source = QLabel(self.tweet['source'])
        label_service_icon = QLabel(self)
        label_service_icon.setPixmap(self.account.service_icon)
        h1.addWidget(label_user)
        #h1.addWidget(label_source)
        h1.addStretch()
        h1.addWidget(label_service_icon)
        
        ## tweet content
        label_tweet = TweetText(self.tweet['text'], self)
        v2.addWidget(label_tweet)
        
        ## retweet if exists
        if('retweeted_status' in self.tweet):
            retweet = self.tweet['retweeted_status']
            
            groupbox = QGroupBox(self)
            #groupbox.setContentsMargins(0, 5, 5, 5)
            v2.addWidget(groupbox)
            v3 = QVBoxLayout()
            v3.setContentsMargins(5, 5, 5, 5)
            groupbox.setLayout(v3)
            
            h3 = QHBoxLayout()
            v3.addLayout(h3)
            label_retweet_user = Text('@' + retweet['user']['screen_name'], self)
            #label_retweet_source = QLabel(retweet['source'])
            h3.addWidget(label_retweet_user)
            #h3.addWidget(label_retweet_source)
            h3.addStretch()
            
            label_retweet = TweetText(retweet['text'], self)
            v3.addWidget(label_retweet)
            
            if(self.thumbnail):
                v3.addWidget(self.thumbnail)
                
            h4 = QHBoxLayout()
            v3.addLayout(h4)
            label_retweet_time = QLabel(retweet['created_at'], self)
            label_retweet_repost = QLabel('转发(%s)' % str(retweet['reposts_count']), self)
            label_retweet_comment = QLabel('评论(%s)' % str(retweet['comments_count']), self)
            h4.addWidget(label_retweet_time)
            h4.addStretch()
            h4.addWidget(label_retweet_repost)
            h4.addWidget(label_retweet_comment)
        ## No retweet and has picture
        elif(self.thumbnail):
            v2.addWidget(self.thumbnail)
        
        #v2.addStretch()
        
        ## time, repost, comment
        h2 = QHBoxLayout()
        v2.addLayout(h2)
        label_tweet_time = QLabel(self.tweet['created_at'], self)
        label_tweet_repost = QLabel('转发(%s)' % str(self.tweet['reposts_count']), self)
        label_tweet_comment = QLabel('评论(%s)' % str(self.tweet['comments_count']), self)
        h2.addWidget(label_tweet_time)
        h2.addStretch()
        h2.addWidget(label_tweet_repost)
        h2.addWidget(label_tweet_comment)
        
#    def paintEvent(self, ev):
#        qp = QPainter()
#        qp.begin(self)
#        rect = self.geometry()
#        qp.drawLine(QPoint(rect.left(), rect.bottom()), QPoint(rect.right(), rect.bottom()))
#        qp.end()
#        return super(TweetWidget, self).paintEvent(ev)