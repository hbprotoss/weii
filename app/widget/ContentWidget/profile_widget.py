# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import logger
from app import easy_thread
from app import account_manager
from app.widget.ContentWidget import abstract_widget

log = logger.getLogger(__name__)

gender = {
    'm': '男',
    'f': '女',
    'n': '未知'
}

class Label(QLabel):
    def __init__(self, text, parent=None):
        super(Label, self).__init__(text, parent)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setWordWrap(True)

class PersonalProfile(QGroupBox):
    '''
    Display single account profile
    '''
    def __init__(self, avatar, user_info, parent=None):
        '''
        @param avatar: path or QPixmap itself
        @param user_info: User Object. see doc
        '''
        super(PersonalProfile, self).__init__(parent)
        self.user_info = user_info
        self.avatar = QPixmap(avatar).scaled(48, 48, transformMode=Qt.SmoothTransformation)
        
        self.setupUI()
#        palette = self.palette()
#        palette.setColor(QPalette.Dark, Qt.white)
#        self.setPalette(palette)
        self.setStyleSheet('''
        QGroupBox {
            margin: 0px;
            padding: 0px;
        }
        ''')
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        
    def setupUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # h1 contains avatar, screen_name ...
        h1 = QHBoxLayout()
        main_layout.addLayout(h1)
        
        avatar_label = QLabel()
        h1.addWidget(avatar_label)
        avatar_label.setPixmap(self.avatar)
        avatar_label.setFixedSize(QSize(48, 48))
        
        h12 = QVBoxLayout()
        h1.addLayout(h12)
        h12.addWidget(QLabel(self.user_info['screen_name']))
        
        h121 = QHBoxLayout()
        h12.addLayout(h121)
        h121.addWidget(QLabel('粉丝: %s' % str(self.user_info['followers_count'])))
        h121.addWidget(QLabel('关注: %s' % str(self.user_info['friends_count'])))
        h121.addWidget(QLabel('微博: %s' % str(self.user_info['statuses_count'])))
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Raised)
        main_layout.addWidget(separator)
        
        h2 = QHBoxLayout()
        main_layout.addLayout(h2)
        h2.addWidget(QLabel('性别: %s' % str(gender[self.user_info['gender']])))
        h2.addWidget(QLabel('位置: %s' % str(self.user_info['location'])))
        
        main_layout.addWidget(QLabel('个人首页:  %s' % self.user_info['url']))
        
        h3 = QHBoxLayout()
        main_layout.addLayout(h3)
        h3.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        label_desc = Label('个人描述:')
        label_desc.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        h3.addWidget(label_desc)
        desc = Label(self.user_info['description'])
        h3.addWidget(desc)

class ProfileWidget(abstract_widget.AbstractWidget):
    '''
    Widget for displaying profile(s)
    '''
    def __init__(self, parent=None):
        super(ProfileWidget, self).__init__(parent)
    
    def appendNew(self):
        pass
    
    def refresh(self):
        self.insertWidget(0, self.retrievingData_image)
        
        log.debug('Starting thread')
        easy_thread.start(self.retrieveData, (account_manager.getCurrentAccount(), ), callback=self.updateUI)
        pass
    
    def updateUI(self, data):
        self.removeAllWidgets()
        for user_info in data:
            if 'error' in user_info:
                QMessageBox.critical(None, user_info['service'], user_info['error'])
            else:
                self.addWidget(PersonalProfile(user_info['avatar_large'], user_info))
    
    def retrieveData(self, account_list):
        rtn = []
        for account in account_list:
            try:
                user_info = account.getUserInfo()
                user_info['avatar_large'] = account.avatar_manager.get(user_info['avatar_large'])
                rtn.append(user_info)
            except Exception as e:
                rtn.append({'error': str(e), 'service': account.plugin.service})
                
        log.debug('Download finished')
        return (rtn,)