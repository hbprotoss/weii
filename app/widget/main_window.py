#!/usr/bin/env python3
# coding=utf-8

import imghdr
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import constant
from app import theme_manager
from app import account_manager
from app.widget import icon_button
from app.widget import stacked_widget
from app.widget.ContentWidget import *

MainWindow_QSS = '''
MainWindow {
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
QToolButton:hover {
    background-color:%s
}
QLabel#account {
    color: white;
    font-size: 16px;
    font-weight: bold;
}
QGroupBox {
    margin-top: 0px;
    padding-top: 0px;
    border-style: solid;
    border-width: 1px;
}
'''

class ButtonGroup:
    '''
    Ensure that only one button can be activated
    '''

    def __init__( self, group, action ):
        '''
        @param group: List of buttons
        @param action: Function object that will be applied to activated button
                        def action(button):
        '''
        self.group = group
        self.action = action
        self.current_button = self.group[0]

    def setActive( self, button ):
        if(button in self.group):
            self.current_button.setStyleSheet( '' )
            self.current_button = button
            self.action( button )
            
    def getCurrent(self):
        return self.current_button
    
class ScrollArea(QScrollArea):
    def resizeEvent(self, ev):
        if(self.verticalScrollBar().isVisible()):
            scrollbar_width = self.verticalScrollBar().width() + 5  # 5 for additional space
        else:
            scrollbar_width = 2 # 2 for additional space
        self.widget().setFixedWidth(self.width() - scrollbar_width)

class MainWindow( QDialog ):
    '''
    Main window for app
    '''

    def __init__( self, parent = None ):
        super( MainWindow, self ).__init__( parent )

        self.setMinimumSize( 400, 600 )
        self.setupUI()
        self.renderUI()
        self.renderUserInfo( account_manager.getCurrentAccount() )
        
        # Show home by default
        self.home.setStyleSheet( 'background-color: %s;' % theme_manager.getParameter('Skin', 'icon-chosen') )
        
        btns = [self.home, self.at, self.comment, self.private, self.profile, self.search]
        self.button_group = ButtonGroup( btns,
            lambda button: button.setStyleSheet('background-color: %s;' %
                    theme_manager.getParameter('Skin', 'icon-chosen')
                    )
            )
        for btn in btns:
            self.connect(btn, SIGNAL('clicked()'), self.onClicked_BtnGroup)
        self.connect(self.refresh, SIGNAL('clicked()'), self.onClicked_BtnRefresh)
        
        # Automatically append new tweets when scrolled nearly to bottom
        self.connect(self.scroll_area.verticalScrollBar(), SIGNAL('valueChanged(int)'), self.onValueChanged_ScrollBar)
    
    def initTab(self):
        '''
        Initiate content tab for home, at, comment, private, profile, search
        @return: A dict of button to widget of QScrollArea
        '''
        rtn = {}
        
        rtn[self.home] = home_widget.HomeWidget(self)
        
        rtn[self.at] = home_widget.HomeWidget(self)
        
        layout = QVBoxLayout()
        layout.addWidget(QPushButton('comment'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.comment] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QPushButton('private'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.private] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QPushButton('profile'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.profile] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QPushButton('search'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.search] = widget
        
        return rtn

    def setupUI( self ):
        '''
        Setup the structure of UI
        '''
        vbox = QVBoxLayout()
        vbox.setContentsMargins( 5, 5, 5, 5 )
        self.setLayout( vbox )

        # Upper, starting with avatar
        h1 = QHBoxLayout()
        vbox.addLayout( h1 )

        # # Left, avatar
        self.avatar = QLabel(self)
        h1.addWidget( self.avatar )
        self.avatar.setMinimumSize( constant.AVATER_SIZE, constant.AVATER_SIZE )
        self.avatar.setSizePolicy( QSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed ) )
        self.avatar.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )

        # # Right
        v11 = QVBoxLayout()
        h1.addLayout( v11 )

        # ## Upper, account
        self.account = QLabel(self)
        self.account.setObjectName( 'account' )
        self.account.setSizePolicy( QSizePolicy( QSizePolicy.Preferred, QSizePolicy.Preferred ) )
        self.account.setCursor( Qt.PointingHandCursor )
        v11.addWidget( self.account )

        # ## Lower
        h111 = QHBoxLayout()
        v11.addLayout( h111 )

        self.fans = QLabel(self)
        h111.addWidget( self.fans )
        self.following = QLabel(self)
        h111.addWidget( self.following )
        self.tweets = QLabel(self)
        h111.addWidget( self.tweets )
        h111.addStretch()

        self.send = icon_button.IconButton(self)
        h111.addWidget( self.send )
        self.refresh = icon_button.IconButton(self)
        h111.addWidget( self.refresh )

        # Lower
        h2 = QHBoxLayout()
        vbox.addLayout( h2 )

        v21 = QVBoxLayout()
        h2.addLayout( v21 )
        self.home = icon_button.IconButton(self)
        v21.addWidget( self.home )
        self.at = icon_button.IconButton(self)
        v21.addWidget( self.at )
        self.comment = icon_button.IconButton(self)
        v21.addWidget( self.comment )
        self.private = icon_button.IconButton(self)
        v21.addWidget( self.private )
        self.profile = icon_button.IconButton(self)
        v21.addWidget( self.profile )
        self.search = icon_button.IconButton(self)
        v21.addWidget( self.search )
        v21.addStretch()
        self.setting = icon_button.IconButton(self)
        v21.addWidget( self.setting )

        ## Scroll area
        self.button_to_widget = self.initTab()
        widget = self.button_to_widget[self.home]
        self.content_widget = stacked_widget.StackedWidget()
        #self.content_widget.setStyleSheet('border-style:solid;border-width:5px')
        for k,v in self.button_to_widget.items():
            self.content_widget.addWidget(v)
        self.content_widget.setCurrentWidget(widget)
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidget( self.content_widget )
        self.scroll_area.setWidgetResizable(True)
        h2.addWidget( self.scroll_area )

    def renderUI( self ):
        '''
        Render UI with specified theme_manager
        @param theme_manager: widget.theme_manager.Theme object
        '''
        self.home.loadIcon( theme_manager.getParameter('Icon', 'home') )
        self.at.loadIcon( theme_manager.getParameter('Icon', 'at'))
        self.comment.loadIcon( theme_manager.getParameter('Icon', 'comment'))
        self.private.loadIcon( theme_manager.getParameter('Icon', 'private'))
        self.profile.loadIcon( theme_manager.getParameter('Icon', 'profile'))
        self.search.loadIcon( theme_manager.getParameter('Icon', 'search'))
        self.send.loadIcon( theme_manager.getParameter('Icon', 'send'))
        self.refresh.loadIcon( theme_manager.getParameter('Icon', 'refresh'))
        self.setting.loadIcon( theme_manager.getParameter('Icon', 'setting'))

        self.setStyleSheet( MainWindow_QSS % ( 
                        theme_manager.getParameter('Skin', 'background-color'),
                        theme_manager.getParameter('Skin', 'background-image'),
                        theme_manager.getParameter('Skin', 'icon-hover')
                        )
        )

    def renderUserInfo( self, account_list ):
        if len(account_list) == 1:
            account = account_list[0]
            user_info = account.plugin.getUserInfo(account.plugin.id)
            avatar = account.avatar_manager.get(user_info['avatar_large'])
            self.avatar.setPixmap( QPixmap(avatar, imghdr.what(avatar)).scaled(constant.AVATER_SIZE, constant.AVATER_SIZE, transformMode=Qt.SmoothTransformation) )
            self.account.setText( str( user_info['screen_name'] ) )
            self.fans.setText( '粉丝(%s)' % str( user_info['followers_count'] ) )
            self.following.setText( '关注(%s)' % str( user_info['friends_count'] ) )
            self.tweets.setText( '微博(%s)' % str( user_info['statuses_count'] ) )
        else:
            self.avatar.setPixmap(QPixmap(constant.DEFAULT_AVATER))
            self.account.setText('全部账户')
            self.fans.setText('粉丝(x)')
            self.following.setText('关注(x)')
            self.tweets.setText('微博(x)')
        
    def showEvent(self, event):
        self.button_to_widget[self.home].refresh()
        
    def onClicked_BtnGroup(self):
        button = self.sender()
        self.button_group.setActive(button)
        
        self.content_widget.setCurrentWidget(self.button_to_widget[button])
    
    def onClicked_BtnRefresh(self):
        button = self.button_group.getCurrent()
        self.button_to_widget[button].refresh()
        
    def onValueChanged_ScrollBar(self, value):
        if value > self.scroll_area.verticalScrollBar().maximum() * 0.9:
            button = self.button_group.getCurrent()
            self.button_to_widget[button].appendNew()