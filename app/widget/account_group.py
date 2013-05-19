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
class AccountGroup(QWidget):
    '''
    Widget to display available accounts. User can choose one of them exclusively.
    '''
    def __init__(self, parent=None):
        super(AccountGroup, self).__init__(parent)
        self.accounts = {}
        
        self.setupUI()
        self.connect(account_manager.signal_emitter, account_manager.SIGNAL_ACCOUNT_ADDED, self.onAccountAdded)
        self.connect(account_manager.signal_emitter, account_manager.SIGNAL_ACCOUNT_DELETED, self.onAccountDeleted)
    
    def setupUI(self):
        self.main_layout = QHBoxLayout()
        
        self.arrow = AccountButton(None)
        self.arrow.setText(LEFT_ARROW)
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
        self.accounts[(account.plugin.service, account.plugin.username)] = acc
        acc.hide()
            
        self.connect(acc, SIGNAL('clicked'), self.onClicked_Account)
        
    def enterEvent(self, ev):
        self.arrow.setText(RIGHT_ARROW)
        for widget in self.accounts.values():
            widget.show()
            
    def leaveEvent(self, ev):
        self.arrow.setText(LEFT_ARROW)
        for widget in self.accounts.values():
            widget.hide()
            
    def onAccountAdded(self, account):
        self.addAccount(account)
    
    def onAccountDeleted(self, account):
        del self.accounts[(account.plugin.service, account.plugin.username)]
        for i in range(self.main_layout.count()):
            widget = self.main_layout.itemAt(i).widget()
            if account is widget.account:
                child = self.main_layout.takeAt(i)
                del child
                return
        
    def onClicked_Account(self, account):
        self.emit(SIGNAL('clicked'), account)
