#!/usr/bin/env python3
#coding=utf-8

import sys
import os
import configparser
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import constant
from app import misc
from widget import Theme
from widget import IconButton

INFO = 'Info'
SKIN = 'Skin'
ICON = 'Icon'
THEME_CONFIG = 'conf.ini'
MainWindow_QSS = '''
QDialog {
background-color:%s;
background-image:url(%s);
background-repeat:no-repeat;
padding: 5px
}
QToolButton {
width:32 px; height:32 px;
border-style: outset;
border-radius: 5px;
}
QLabel#account {
color: white;
font-size: 16px;
font-weight: bold;
}
'''

class MainWindow(QDialog):
    '''
    Main window for app
    '''
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.setMinimumSize(400, 600)
        self.setupUI()
        self.theme = self.loadTheme('default')
        self.renderUI(self.theme)
        self.renderUserInfo(QPixmap(constant.DEFAULT_AVATER), '全部账户', 0, 0, 0)
        self.home.setStyleSheet('background-color: rgb(255, 170, 0);')
        pass
    
    def setupUI(self):
        '''
        Setup the structure of UI
        '''
        vbox = QVBoxLayout()
        vbox.setContentsMargins(5, 5, 5, 5)
        self.setLayout(vbox)
        
        # Upper, starting with avater
        h1 = QHBoxLayout()
        vbox.addLayout(h1)
        
        ## Left, avater
        self.avater = QLabel()
        h1.addWidget(self.avater)
        self.avater.setMinimumSize(64, 64)
        self.avater.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.avater.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        ## Right
        v11 = QVBoxLayout()
        h1.addLayout(v11)
        
        ### Upper, account
        self.account = QLabel()
        self.account.setObjectName('account')
        self.account.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.account.setCursor(Qt.PointingHandCursor)
        v11.addWidget(self.account)
        
        ### Lower
        h111 = QHBoxLayout()
        v11.addLayout(h111)
        
        self.fans = QLabel()
        h111.addWidget(self.fans)
        self.following = QLabel()
        h111.addWidget(self.following)
        self.tweets = QLabel()
        h111.addWidget(self.tweets)
        h111.addStretch()
        
        self.send = IconButton.IconButton()
        h111.addWidget(self.send)
        self.refresh = IconButton.IconButton()
        h111.addWidget(self.refresh)
        
        # Lower
        h2 = QHBoxLayout()
        vbox.addLayout(h2)
        
        v21 = QVBoxLayout()
        h2.addLayout(v21)
        self.home = IconButton.IconButton()
        v21.addWidget(self.home)
        self.at = IconButton.IconButton()
        v21.addWidget(self.at)
        self.comment = IconButton.IconButton()
        v21.addWidget(self.comment)
        self.private = IconButton.IconButton()
        v21.addWidget(self.private)
        self.profile = IconButton.IconButton()
        v21.addWidget(self.profile)
        self.search = IconButton.IconButton()
        v21.addWidget(self.search)
        v21.addStretch()
        
        ## Scroll area
        self.content_layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(self.content_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        h2.addWidget(scroll_area)
        
        pass
    
    def loadTheme(self, theme_name='default'):
        '''
        @param theme_name: The name of theme
        @return: Theme.Theme object
        '''
        THEME_ROOT = os.path.join(constant.APP_ROOT, 'theme', theme_name)
        ICON_ROOT = os.path.join(THEME_ROOT, 'icon')
        conf = misc.ConfParser()
        conf.read(os.path.join(THEME_ROOT, THEME_CONFIG))
        
        theme = Theme.Theme()
        theme.info = dict(conf.items(INFO))
        theme.skin = dict(conf.items(SKIN))
        theme.skin['background-image'] = os.path.join(THEME_ROOT, theme.skin['background-image'])
        theme.icon = {k:os.path.join(ICON_ROOT, v) for k,v in conf.items(ICON)}
        theme.path = THEME_ROOT
        
        return theme
    
    def renderUI(self, theme):
        '''
        Render UI with specified theme
        @param theme: Theme.Theme object
        '''
        self.home.loadIcon(theme.icon['home'])
        self.at.loadIcon(theme.icon['at'])
        self.comment.loadIcon(theme.icon['comment'])
        self.private.loadIcon(theme.icon['private'])
        self.profile.loadIcon(theme.icon['profile'])
        self.search.loadIcon(theme.icon['search'])
        self.send.loadIcon(theme.icon['send'])
        self.refresh.loadIcon(theme.icon['refresh'])
        
        self.setStyleSheet(MainWindow_QSS % (
                        theme.skin['background-color'],
                        theme.skin['background-image']
                        ))
        pass
    
    def renderUserInfo(self, avater, account_name, fans, following, tweets):
        self.avater.setPixmap(avater)
        self.account.setText(str(account_name))
        self.fans.setText('粉丝(%s)' % str(fans))
        self.following.setText('关注(%s)' % str(following))
        self.tweets.setText('微博(%s)' % str(tweets))