# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app.widget import stacked_widget
from app import account_manager
from app import plugin

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, parent, strings):
        super(TreeWidgetItem, self).__init__(parent, strings)
        
    def __hash__(self):
        return id(self)

class SettingWindow(QDialog):
    '''
    Main setting window
    '''
    def __init__(self, parent=None):
        super(SettingWindow, self).__init__(parent)
        
        # QTreeWidgetItem to content widget
        self.item_to_widget = {}
        
        self.setMinimumSize(600, 400)
        self.setupUI()
        
        self.addAccountOption()
        self.expandFirstLayer()
        
        item = self.tree_widget.topLevelItem(0)
        self.content_widget.setCurrentWidget(self.item_to_widget[item])
        
    def setupUI(self):
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        
        # Left tree widget
        self.tree_widget = QTreeWidget()
        hbox.addWidget(self.tree_widget)
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderHidden(True)
        tree_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tree_size_policy.setHorizontalStretch(2)
        self.tree_widget.setSizePolicy(tree_size_policy)
        
        # Right stacked widget
        self.content_widget = stacked_widget.StackedWidget()
        hbox.addWidget(self.content_widget)
        content_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_size_policy.setHorizontalStretch(5)
        self.content_widget.setSizePolicy(content_size_policy)
        
    def expandFirstLayer(self):
        for i in range(self.tree_widget.topLevelItemCount()):
            self.tree_widget.setItemExpanded(self.tree_widget.topLevelItem(i), True)
        
    def addAccountOption(self):
        def addAccount(account):
            '''
            @param account: account_manager.Account object
            '''
            item = TreeWidgetItem(self.account_option, [account.plugin.username])
            item.setIcon(0, QIcon(QPixmap.fromImage(account.service_icon)))

            
        self.account_option = TreeWidgetItem(self.tree_widget, ['账户'])
        self.tree_widget.addTopLevelItem(self.account_option)
        widget = AccountOptionWidget()
        self.item_to_widget[self.account_option] = widget
        self.content_widget.addWidget(widget)
        
        for account in account_manager.getAllAccount():
            addAccount(account)
            
class AccountOptionWidget(QWidget):
    '''
    List how many plugins are available and guide user to create a new account. 
    '''
    
    def __init__(self, parent=None):
        super(AccountOptionWidget, self).__init__(parent)
        
        self.setupUI()
        self.initItems()
        
        self.connect(self.add_button, SIGNAL('clicked()'), self.onClicked_BtnAdd)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        
        self.list_widget = QListWidget()
        vbox.addWidget(self.list_widget)
        
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        #hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(QLabel('请注意，Web认证页面通过全局代理设置来连接'))
        hbox.addStretch()
        self.add_button = QPushButton('添加')
        hbox.addWidget(self.add_button)
        
    def initItems(self):
        for name, plugin_module in plugin.plugins.items():
            item = QListWidgetItem(
                QIcon(QPixmap(plugin_module.Plugin.service_icon)),
                name,
                self.list_widget
            )
            
    def onClicked_BtnAdd(self):
        #QMessageBox.information(self, '', str(self.list_widget.currentRow()))
        item = self.list_widget.currentItem()
        if item:
            print(item.text())
            
    def addAccount(self, service):
        pass