# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import account_manager
from app import constant

class AccountStruct:
    '''
    Dummy class of account_manager.Account. Serving for 'all_accounts'
    '''
    class Plugin:
        service = 'all_accounts'
        username = 'all_accounts'
    plugin = Plugin()

class LabelButton(QLabel):
    def __init__(self, *argv):
        super(LabelButton, self).__init__(*argv)
        self.setCursor(Qt.PointingHandCursor)
        
    def mouseReleaseEvent(self, ev):
        self.emit(SIGNAL('clicked()'))
        
class AccountButton(LabelButton):
    def __init__(self, account, parent=None):
        super(AccountButton, self).__init__(parent)
        self.account = account
        
    def mouseReleaseEvent(self, ev):
        self.emit(SIGNAL('clicked'), self.account)
            
LEFT_ARROW = '◀'
RIGHT_ARROW = '▶'
ARROWS = [LEFT_ARROW, RIGHT_ARROW]
class AccountGroup(QWidget):
    '''
    Widget to display available accounts. User can choose one of them exclusively.
    '''
    def __init__(self, parent=None):
        super(AccountGroup, self).__init__(parent)
        self.arrow_index = 0
        self.accounts = {}
        
        self.setupUI()
        self.connect(self.arrow, SIGNAL('clicked()'), self.onClicked_Arrow)
    
    def setupUI(self):
        self.main_layout = QHBoxLayout()
        
        self.arrow = LabelButton(ARROWS[self.arrow_index])
        self.main_layout.addWidget(self.arrow)
        
        self.all_account = AccountButton(AccountStruct())
        self.all_account.setPixmap(QPixmap(constant.ALL_ACCOUNTS))
        self.all_account.setToolTip('所有账户')
        self.accounts['all_accounts'] = self.all_account
        self.all_account.hide()
        self.connect(self.all_account, SIGNAL('clicked'), self.onClicked_Account)
        self.main_layout.addWidget(self.all_account)
        
        self.setLayout(self.main_layout)
        
    def addAccount(self, account):
        '''
        @param account: account_manager.Account ojbect
        '''
        acc = AccountButton(account)
        acc.setPixmap(QPixmap.fromImage(account.service_icon))
        acc.setToolTip(account.plugin.username)
        self.main_layout.addWidget(acc)
        self.accounts[account.plugin.username] = acc
        if self.arrow_index == 0:
            acc.hide()
            
        self.connect(acc, SIGNAL('clicked'), self.onClicked_Account)
        
    def onClicked_Arrow(self):
        self.arrow_index = 1 - self.arrow_index
        self.arrow.setText(ARROWS[self.arrow_index])
        if self.arrow_index == 0:
            for username, widget in self.accounts.items():
                widget.hide()
        else:
            for username, widget in self.accounts.items():
                widget.show()
                
    def onClicked_Account(self, account):
        self.emit(SIGNAL('clicked'), account)
