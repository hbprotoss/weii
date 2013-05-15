#!/usr/bin/env python3
# coding=utf-8

import imghdr
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import constant, easy_thread
from app import theme_manager
from app import account_manager
from app import logger
from app.widget import icon_button
from app.widget import stacked_widget
from app.widget import setting_window
from app.widget import new_tweet_window
from app.widget import account_group
from app.widget.ContentWidget import *

log = logger.getLogger(__name__)

# TODO: round-corner tooltip
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
'''

SIGNAL_UPDATE_UNREADS = SIGNAL('updateUnreads')

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

        self.setWindowTitle('weii')
        self.setupTray()
        self.setMinimumSize( 400, 600 )
        self.setupUI()
        self.renderUI()
        self.renderUserInfo()
        
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
            
        # Refresh button clicked
        self.connect(self.refresh, SIGNAL('clicked()'), self.onClicked_BtnRefresh)
        # Setting button clicked
        self.connect(self.setting, SIGNAL('clicked()'), self.onClicked_BtnSetting)
        # Sending button clicked
        self.connect(self.send, SIGNAL('clicked()'), self.onClicked_BtnSending)
        
        # Automatically append new tweets when scrolled nearly to bottom
        self.connect(self.scroll_area.verticalScrollBar(), SIGNAL('valueChanged(int)'), self.onValueChanged_ScrollBar)
        # Update account info
        self.connect(account_manager.getEmitter(), account_manager.SIGNAL_ACCOUNT_ADDED,
            lambda x:self.renderUserInfo()
        )
        
        # Account group
        self.connect(self.account_group, SIGNAL('clicked'), self.onClicked_AccountGroup)
        
    
    def initTab(self, content_widget):
        '''
        Initiate content tab for home, at, comment, private, profile, search
        @return: A dict of button to widget of QScrollArea
        '''
        rtn = {}
        
        rtn[self.home] = home_widget.HomeWidget(content_widget)
        rtn[self.at] = at_widget.AtWidget(content_widget)
        rtn[self.comment] = comment_widget.CommentWidget(content_widget)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('正在建设中...'))
        widget = QWidget()
        widget.setLayout(layout)
        rtn[self.private] = widget
        
        rtn[self.profile] = profile_widget.ProfileWidget(content_widget) 
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel('正在建设中...'))
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

        # ## Upper, account name
        h21 = QHBoxLayout()
        self.account = QLabel(self)
        self.account.setObjectName( 'account' )
        self.account.setSizePolicy( QSizePolicy( QSizePolicy.Preferred, QSizePolicy.Preferred ) )
        #self.account.setCursor( Qt.PointingHandCursor )
        h21.addWidget(self.account)
        
        h21.addStretch()
        
        # ## Upper, account group
        self.account_group = account_group.AccountGroup()
        for acc in account_manager.getAllAccount():
            self.account_group.addAccount(acc)
        h21.addWidget(self.account_group)
        v11.addLayout(h21)

        # ## Lower
        h22 = QHBoxLayout()
        v11.addLayout( h22 )

        self.fans = QLabel(self)
        h22.addWidget( self.fans )
        self.following = QLabel(self)
        h22.addWidget( self.following )
        self.tweets = QLabel(self)
        h22.addWidget( self.tweets )
        h22.addStretch()

        self.send = icon_button.IconButton(self)
        self.send.setToolTip('新消息')
        h22.addWidget( self.send )
        self.refresh = icon_button.IconButton(self)
        self.refresh.setToolTip('刷新')
        h22.addWidget( self.refresh )

        # Lower
        h2 = QHBoxLayout()
        vbox.addLayout( h2 )

        v21 = QVBoxLayout()
        h2.addLayout( v21 )
        self.home = icon_button.IconButton(self)
        self.home.setToolTip('主页')
        v21.addWidget( self.home )
        self.at = icon_button.IconButton(self)
        self.at.setToolTip('AT')
        v21.addWidget( self.at )
        self.comment = icon_button.IconButton(self)
        self.comment.setToolTip('评论')
        v21.addWidget( self.comment )
        self.private = icon_button.IconButton(self)
        self.private.setToolTip('私信')
        v21.addWidget( self.private )
        self.profile = icon_button.IconButton(self)
        self.profile.setToolTip('档案')
        v21.addWidget( self.profile )
        self.search = icon_button.IconButton(self)
        self.search.setToolTip('搜索')
        v21.addWidget( self.search )
        v21.addStretch()
        self.setting = icon_button.IconButton(self)
        self.setting.setToolTip('设置')
        v21.addWidget( self.setting )

        ## Scroll area
        self.content_widget = stacked_widget.StackedWidget()
        self.button_to_widget = self.initTab(self.content_widget)
        widget = self.button_to_widget[self.home]
        
        # set background color
        self.content_widget.setStyleSheet('background-color:#f4f4f2')
        self.content_widget.setAutoFillBackground(True)
        self.content_widget.show()
        #self.content_widget.setStyleSheet('border-style:solid;border-width:5px')
        
        for k,v in self.button_to_widget.items():
            self.content_widget.addWidget(v)
        self.content_widget.setCurrentWidget(widget)
        self.scroll_area = ScrollArea()
        self.scroll_area.setWidget( self.content_widget )
        self.scroll_area.setWidgetResizable(True)
        h2.addWidget( self.scroll_area )
        
    def setupTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(constant.TRAY_ICON))
        self.tray_icon.show()

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

    def renderUserInfo(self):
        account_list = account_manager.getCurrentAccount()
        if len(account_list) == 1:
            account = account_list[0]
            user_info = account.plugin.getUserInfo(account.plugin.uid)
            avatar = account.avatar_manager.get(user_info['avatar_large'])
            self.updateUserInfo(
                avatar,
                user_info
            )
        else:
            self.updateUserInfo(constant.ALL_ACCOUNTS_AVATAR,
                {
                    'screen_name': '全部账户',
                    'followers_count': 'x', 
                    'friends_count': 'x',
                    'statuses_count': 'x'
                }
            )
            
    def updateUserInfo(self, avatar, user_info):
        '''
        @param user_info: Object returned by plugin.getUserInfo
        '''
        self.avatar.setPixmap(QPixmap(avatar, imghdr.what(avatar)).scaled(constant.AVATER_SIZE, constant.AVATER_SIZE, transformMode=Qt.SmoothTransformation))
        self.account.setText(user_info['screen_name'])
        self.fans.setText('粉丝(%s)' % user_info['followers_count'])
        self.following.setText('关注(%s)' % user_info['friends_count'])
        self.tweets.setText('微博(%s)' % user_info['statuses_count'])
        
    def showEvent(self, event):
        self.button_to_widget[self.home].initialRefresh()
        self.button_to_widget[self.comment].initialRefresh()
        self.button_to_widget[self.at].initialRefresh()
        easy_thread.start(self.checkUnreads)
        self.connect(self, SIGNAL_UPDATE_UNREADS, self.updateUnreads)
        
    def checkUnreads(self):
        '''
        Check unread message count.
        '''
        # Only availabel for single account.
        while True:
            unreads = {
                'tweet': 0,
                'mention': 0,
                'comment': 0,
                'follower': 0,
                'private': 0
            }
            for account in account_manager.getCurrentAccount():
                acc_unreads = account.plugin.getUnreads()
                log.info('%s, %s, %s' % (account.plugin.service, account.plugin.username, acc_unreads))
                for key in unreads.keys():
                    unreads[key] += acc_unreads[key]
            self.emit(SIGNAL_UPDATE_UNREADS, unreads)
            QThread.sleep(60)
        
    def updateUnreads(self, unreads):
        self.home.setBuble(int(unreads['tweet']))
        self.at.setBuble(int(unreads['mention']))
        self.comment.setBuble(int(unreads['comment']))
        self.private.setBuble(int(unreads['private']))
        self.profile.setBuble(int(unreads['follower']))
        
    def onClicked_BtnGroup(self):
        button = self.sender()
        button.setBuble(0)
        self.button_group.setActive(button)
        
        new_widget = self.button_to_widget[button]
        old_widget = self.content_widget.currentWidget()
        slider = self.scroll_area.verticalScrollBar()
        self.content_widget.setScrollPosition(old_widget, slider.sliderPosition())
        
        self.content_widget.setCurrentWidget(new_widget)
        slider.setSliderPosition(self.content_widget.getScrollPosition(new_widget))
        
        #new_widget.refresh()
        #self.onClicked_BtnRefresh()
    
    def onClicked_BtnRefresh(self):
        button = self.button_group.getCurrent()
        self.button_to_widget[button].refresh()
        self.scroll_area.verticalScrollBar().setSliderPosition(0)
        
    def onClicked_BtnSetting(self):
        window = setting_window.SettingWindow()
        window.exec()
        
    def onClicked_BtnSending(self):
        window = new_tweet_window.NewTweetWindow(self)
        
        rect = self.geometry()
        screen_rect = QApplication.desktop().availableGeometry()
        size = window.size()
        
        # Horizontal position
        if rect.right() + size.width() > screen_rect.right():
            left = rect.left() - size.width()
        else:
            left = rect.right()
        # Vertical position
        if rect.top() + size.height() > screen_rect.bottom():
            top = screen_rect.bottom() - size.height()
        else:
            top = rect.top()
            
        window.setGeometry(QRect(left, top, window.width(), window.height()))
        window.show()
        
    def onClicked_AccountGroup(self, account):
        def getUserInfo(account):
            try:
                if account.plugin.service == 'all_accounts':
                    user_info = {
                        'screen_name': '所有账户',
                        'followers_count': 'x',
                        'friends_count': 'x',
                        'statuses_count': 'x'
                    }
                    avatar = constant.ALL_ACCOUNTS_AVATAR
                else:
                    user_info = account.getUserInfo(account.plugin.uid)
                    avatar = account.avatar_manager.get(user_info['avatar_large'])
                return (avatar, user_info)
            except Exception as e:
                return (None, {'error': str(e), 'service': account.plugin.service})
            
        def updateUI(avatar, user_info):
            if 'error' in user_info:
                QMessageBox.critical(None, user_info['service'], user_info['error'])
            else:
                self.updateUserInfo(avatar, user_info)
                self.button_to_widget[self.button_group.getCurrent()].refresh()
        
        account_manager.setCurrentAccount(account.plugin.service, account.plugin.username)
        easy_thread.start(getUserInfo,
            args=(account, ),
            callback=updateUI
        )
        
#        widget = self.button_to_widget[self.button_group.getCurrent()]
#        widget.refresh()
        
    def onValueChanged_ScrollBar(self, value):
        if value > self.scroll_area.verticalScrollBar().maximum() * 0.9:
            button = self.button_group.getCurrent()
            self.button_to_widget[button].appendNew()