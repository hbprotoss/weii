# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app.widget import tweet_widget

class SeperatedTweetWindow(QDialog):
    def __init__(self, account, tweet, avatar, thumbnail, parent=None):
        super(SeperatedTweetWindow, self).__init__(parent)
        self.account = account
        self.tweet = tweet
        self.avatar = avatar
        self.thumbnail = thumbnail
        
        self.setupUI()
        
    def setupUI(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.addWidget(tweet_widget.TweetWidget(self.account, self.tweet, self.avatar, self.thumbnail))