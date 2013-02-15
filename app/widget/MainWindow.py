#!/usr/bin/env python3
# coding=utf-8

import sys
import os
import configparser
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import constant
from app import misc
from widget import Theme
from widget import IconButton
from widget.ContentWidget import *

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
QToolButton:hover {
background-color:%s
}
QLabel#account {
color: white;
font-size: 16px;
font-weight: bold;
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

class MainWindow( QDialog ):
    '''
    Main window for app
    '''

    def __init__( self, parent = None ):
        super( MainWindow, self ).__init__( parent )

        self.setMinimumSize( 400, 600 )
        self.setupUI()
        self.theme = self.loadTheme( 'default' )
        self.renderUI( self.theme )
        self.renderUserInfo( QPixmap( constant.DEFAULT_AVATER ), '全部账户', 0, 0, 0 )
        self.home.setStyleSheet( 'background-color: %s;' % self.theme.skin['icon-chosen'] )
        btns = [self.home, self.at, self.comment, self.private, self.profile, self.search]
        self.button_group = ButtonGroup( btns,
                            lambda button: button.setStyleSheet('background-color: %s;' % self.theme.skin['icon-chosen'])
                            )
        for btn in btns:
            self.connect(btn, SIGNAL('clicked()'), self.onClicked_BtnGroup)
        self.connect(self.refresh, SIGNAL('clicked()'), self.onClicked_BtnRefresh)
    
    def initTab(self):
        '''
        Initiate content tab for home, at, comment, private, profile, search
        @return: A dict of button to widget of QScrollArea
        '''
        rtn = {}
        
        rtn[self.home] = HomeWidget.HomeWidget()
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('at'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.at] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('comment'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.comment] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('private'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.private] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('profile'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.profile] = widget
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('search'))
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

        # Upper, starting with avater
        h1 = QHBoxLayout()
        vbox.addLayout( h1 )

        # # Left, avater
        self.avater = QLabel()
        h1.addWidget( self.avater )
        self.avater.setMinimumSize( 64, 64 )
        self.avater.setSizePolicy( QSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed ) )
        self.avater.setAlignment( Qt.AlignHCenter | Qt.AlignVCenter )

        # # Right
        v11 = QVBoxLayout()
        h1.addLayout( v11 )

        # ## Upper, account
        self.account = QLabel()
        self.account.setObjectName( 'account' )
        self.account.setSizePolicy( QSizePolicy( QSizePolicy.Preferred, QSizePolicy.Preferred ) )
        self.account.setCursor( Qt.PointingHandCursor )
        v11.addWidget( self.account )

        # ## Lower
        h111 = QHBoxLayout()
        v11.addLayout( h111 )

        self.fans = QLabel()
        h111.addWidget( self.fans )
        self.following = QLabel()
        h111.addWidget( self.following )
        self.tweets = QLabel()
        h111.addWidget( self.tweets )
        h111.addStretch()

        self.send = IconButton.IconButton()
        h111.addWidget( self.send )
        self.refresh = IconButton.IconButton()
        h111.addWidget( self.refresh )

        # Lower
        h2 = QHBoxLayout()
        vbox.addLayout( h2 )

        v21 = QVBoxLayout()
        h2.addLayout( v21 )
        self.home = IconButton.IconButton()
        v21.addWidget( self.home )
        self.at = IconButton.IconButton()
        v21.addWidget( self.at )
        self.comment = IconButton.IconButton()
        v21.addWidget( self.comment )
        self.private = IconButton.IconButton()
        v21.addWidget( self.private )
        self.profile = IconButton.IconButton()
        v21.addWidget( self.profile )
        self.search = IconButton.IconButton()
        v21.addWidget( self.search )
        v21.addStretch()

        ## Scroll area
        self.button_to_widget = self.initTab()
        widget = self.button_to_widget[self.home]
        self.content_widget = QStackedWidget()
        #self.content_widget.setStyleSheet('border-style:solid;border-width:5px')
        for k,v in self.button_to_widget.items():
            self.content_widget.addWidget(v)
        self.content_widget.setCurrentWidget(widget)
        scroll_area = QScrollArea()
        scroll_area.setWidget( self.content_widget )
        scroll_area.setWidgetResizable(True)
        h2.addWidget( scroll_area )

        pass

    def loadTheme( self, theme_name = 'default' ):
        '''
        @param theme_name: The name of theme
        @return: Theme.Theme object
        '''
        THEME_ROOT = os.path.join( constant.APP_ROOT, 'theme', theme_name )
        ICON_ROOT = os.path.join( THEME_ROOT, 'icon' )
        conf = misc.ConfParser()
        conf.read( os.path.join( THEME_ROOT, THEME_CONFIG ) )

        theme = Theme.Theme()
        theme.info = dict( conf.items( INFO ) )
        theme.skin = dict( conf.items( SKIN ) )
        theme.skin['background-image'] = os.path.join( THEME_ROOT, theme.skin['background-image'] )
        theme.icon = {k:os.path.join( ICON_ROOT, v ) for k, v in conf.items( ICON )}
        theme.path = THEME_ROOT

        return theme

    def renderUI( self, theme ):
        '''
        Render UI with specified theme
        @param theme: Theme.Theme object
        '''
        self.home.loadIcon( theme.icon['home'] )
        self.at.loadIcon( theme.icon['at'] )
        self.comment.loadIcon( theme.icon['comment'] )
        self.private.loadIcon( theme.icon['private'] )
        self.profile.loadIcon( theme.icon['profile'] )
        self.search.loadIcon( theme.icon['search'] )
        self.send.loadIcon( theme.icon['send'] )
        self.refresh.loadIcon( theme.icon['refresh'] )

        self.setStyleSheet( MainWindow_QSS % ( 
                        theme.skin['background-color'],
                        theme.skin['background-image'],
                        theme.skin['icon-hover']
                        ) )
        pass

    def renderUserInfo( self, avater, account_name, fans, following, tweets ):
        self.avater.setPixmap( avater )
        self.account.setText( str( account_name ) )
        self.fans.setText( '粉丝(%s)' % str( fans ) )
        self.following.setText( '关注(%s)' % str( following ) )
        self.tweets.setText( '微博(%s)' % str( tweets ) )
        
    def onClicked_BtnGroup(self):
        button = self.sender()
        self.button_group.setActive(button)
        
        self.content_widget.setCurrentWidget(self.button_to_widget[button])
    
    def onClicked_BtnRefresh(self):
        button = self.button_group.getCurrent()
        self.button_to_widget[button].refresh([])