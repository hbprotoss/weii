# coding=utf-8

import json

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyQt4.QtWebKit import *

from app.widget import stacked_widget
from app import account_manager
from app import config_manager
from app import plugin
from app import logger
from app import easy_thread
import urllib

log = logger.getLogger(__name__)

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
        self.setWindowTitle('设置')
        
        # QTreeWidgetItem to content widget
        self.item_to_widget = {}
        
        self.setMinimumSize(600, 400)
        self.setupUI()
        
        self.addAccountOption()
        self.expandFirstLayer()
        
        # Tree item clicked
        self.connect(self.tree_widget, SIGNAL('itemClicked (QTreeWidgetItem *,int)'), self.onItemClicked_Tree)
        # Account deleted
        self.connect(account_manager.getEmitter(), account_manager.SIGNAL_ACCOUNT_DELETED, self.onAccountDelete)
        
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
            
    def onItemClicked_Tree(self, tree_widget_item, column):
        self.content_widget.setCurrentWidget(self.item_to_widget[tree_widget_item])
        
    def onAccountDelete(self, account):
        for i in range(self.account_option.childCount()):
            item = self.account_option.child(i)
            dst_account = self.item_to_widget[item].account
            
            # Service and id match
            if (dst_account.plugin.service == account.plugin.service) and \
                    (dst_account.plugin.uid == account.plugin.uid):
                self.tree_widget.setCurrentItem(self.account_option)
                self.account_option.removeChild(item)
                self.content_widget.removeWidget(self.item_to_widget[item])
                del self.item_to_widget[item]
                del item
                break
        pass
        
    def addAccountOption(self):
        def addAccount(account):
            '''
            @param account: account_manager.Account object
            '''
            item = TreeWidgetItem(self.account_option, [account.plugin.username])
            item.setIcon(0, QIcon(QPixmap.fromImage(account.service_icon)))
            widget = SingleAccountWidget(account)
            self.item_to_widget[item] = widget
            self.content_widget.addWidget(widget)

            
        self.account_option = TreeWidgetItem(self.tree_widget, ['账户'])
        self.tree_widget.addTopLevelItem(self.account_option)
        widget = AccountOptionWidget()
        self.item_to_widget[self.account_option] = widget
        self.content_widget.addWidget(widget)
        
        # Receive signal
        self.connect(account_manager.getEmitter(), account_manager.SIGNAL_ACCOUNT_ADDED, addAccount)
        
        for account in account_manager.getAllAccount():
            addAccount(account)
            
class WebView(QDialog):
    '''
    Display a web page for user to authorize app.
    '''
    def __init__(self, url, callback_url, parent=None):
        super(WebView, self).__init__(parent)
        self.url = url
        self.callback_url = callback_url
        self.redirected_url = QUrl()
        
        global_proxy = json.loads(config_manager.getParameter('Proxy'))
        if len(global_proxy.keys()) != 0:
            proxy_string = global_proxy['http']
            (host_name, port) = proxy_string.rsplit(':', 1)
            #host_name = host_name.split('://')[-1]
            
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(host_name)
            proxy.setPort(int(port))
            QNetworkProxy.setApplicationProxy(proxy)
        
        self.setupUI()
        self.connect(self.web, SIGNAL('urlChanged (const QUrl&)'), self.onUrlChange)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        
        self.web = QWebView()
        self.web.load(QUrl(self.url))
        self.web.show()
        vbox.addWidget(self.web)
        
    def onUrlChange(self, url):
        #log.debug(url.toString())
        if url.toString().startswith(self.callback_url):
            self.redirected_url = url
            self.close()
        
    def getRedirectedUrl(self):
        return self.redirected_url.toString()
    

class AccountOptionWidget(QWidget):
    '''
    List how many plugins are available and guide user to create a new account. 
    
    PyQt signal:
    AccountAdded:
        @param account: : account_manager.Account object
    '''
    
    def __init__(self, parent=None):
        super(AccountOptionWidget, self).__init__(parent)
        
        self.setupUI()
        self.initItems()
        
        self.connect(self.btn_add, SIGNAL('clicked()'), self.onClicked_BtnAdd)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        
        vbox.addWidget(QLabel('插件列表'))
        
        self.list_widget = QListWidget()
        vbox.addWidget(self.list_widget)
        
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        #hbox.setAlignment(Qt.AlignRight)
        hbox.addWidget(QLabel('请注意，Web认证页面通过全局代理设置来连接'))
        hbox.addStretch()
        self.btn_add = QPushButton('添加')
        hbox.addWidget(self.btn_add)
        
    def updateUI(self, service, access_token, access_token_secret):
        self.btn_add.setText('添加')
        self.btn_add.setEnabled(True)
        
        # SQLite objects created in a thread can only be used in that same thread.
        acc = account_manager.addAccount(service, '', '', access_token, access_token_secret, config_manager.getParameter('Proxy'))
        log.info('Account(%s, %s) added.' % (acc.plugin.service, acc.plugin.username))
        
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
            self.btn_add.setText('添加账户中...')
            self.btn_add.setEnabled(False)
            
            log.debug(item.text())
            self.addAccount(item.text())
            
    def retrieveData(self, service, redirected_url, plugin_class, proxy):
        url, data, headers = plugin_class.getAccessToken(redirected_url)
        opener = urllib.request.URLopener(proxy)
        for k,v in headers.items():
            opener.addheader(k, v)
        f = opener.open(url, data)
        data = f.read().decode('utf-8')
        log.debug(data)
        
        # Parse returned data.
        access_token, access_token_secret = plugin_class.parseData(data)
        
        return (service, access_token, access_token_secret), {}
            
    def addAccount(self, service):
        '''
        @param service: string. Service name
        '''
        # Visit authorize url and get redirected url.
        plugin_class = plugin.plugins[service].Plugin
        url = plugin_class.getAuthorize()
        callback = plugin_class.getCallbackUrl()
        web = WebView(url, callback)
        web.exec()
        
        # Visit access token url.
        redirected_url = web.getRedirectedUrl()
        log.debug(redirected_url)
        # User gives up adding account
        if redirected_url == '':
            self.btn_add.setText('添加')
            self.btn_add.setEnabled(True)
            return None
        
        easy_thread.start(self.retrieveData, args=(service, redirected_url, plugin_class, global_proxy),
            callback=self.updateUI
        )
    
class SingleAccountWidget(QWidget):
    '''
    Widget for single account setting
    '''
    def __init__(self, account, parent=None):
        '''
        @param account: account_manager.Account object
        '''
        super(SingleAccountWidget, self).__init__(parent)
        self.account = account
        
        self.setupUI()
        # Proxy changed
        self.connect(self.CheckBox_proxy, SIGNAL('stateChanged (int)'), self.onStateChanged_checkbox)
        # Delete account
        self.connect(self.btn_delete, SIGNAL('clicked()'), self.onClicked_BtnDelete)
        
        # Set proxy initial state
        if 'https' in self.account.plugin.proxy:
            self.CheckBox_proxy.setCheckState(Qt.Checked)
            proxy = self.account.plugin.proxy['https'].split('://')[-1]
            host, port = proxy.split(':')
            self.edit_host.setText(host)
            self.edit_port.setText(port)
        else:
            self.CheckBox_proxy.setCheckState(Qt.Unchecked)
            self.onStateChanged_checkbox(Qt.Unchecked)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        
        # Proxy setting
        self.CheckBox_proxy = QCheckBox('设置代理')
        self.CheckBox_proxy.setCheckState(Qt.Checked)
        vbox.addWidget(self.CheckBox_proxy)
        
        proxy_layout = QHBoxLayout()
        vbox.addLayout(proxy_layout)
        label_host = QLabel('服务器:')
        label_host.setStyleSheet('margin-left: 10px')
        proxy_layout.addWidget(label_host)
        self.edit_host = QLineEdit()
        proxy_layout.addWidget(self.edit_host)
        label_port = QLabel('端口:')
        label_port.setStyleSheet('margin-left: 5px')
        proxy_layout.addWidget(label_port)
        self.edit_port = QLineEdit()
        proxy_layout.addWidget(self.edit_port)
        
        
        vbox.addStretch()
        
        # Bottom button
        button_layout = QHBoxLayout()
        vbox.addLayout(button_layout)
        self.btn_delete = QPushButton('删除账户')
        button_layout.addWidget(self.btn_delete)
        button_layout.addStretch()
        self.btn_apply = QPushButton('应用')
        button_layout.addWidget(self.btn_apply)
        
    def onStateChanged_checkbox(self, checked):
        if checked:
            self.edit_host.setEnabled(True)
            self.edit_port.setEnabled(True)
        else:
            self.edit_host.setEnabled(False)
            self.edit_port.setEnabled(False)
            
    def onClicked_BtnDelete(self):
        account_manager.deleteAccount(self.account)