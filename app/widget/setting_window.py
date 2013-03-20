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
            
class WebView(QDialog):
    def __init__(self, url, callback_url, parent=None):
        super(WebView, self).__init__(parent)
        self.url = url
        self.callback_url = callback_url
        self.redirected_url = QUrl()
        
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
        log.debug(url.toString())
        if url.toString().startswith(self.callback_url):
            self.redirected_url = url
            self.close()
        
    def getRedirectedUrl(self):
        return self.redirected_url.toString()

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
            log.debug(item.text())
            self.addAccount(item.text())
            
    def addAccount(self, service):
        global_proxy = json.loads(config_manager.getParameter('Proxy'))
        if len(global_proxy.keys()) != 0:
            proxy_string = global_proxy['http']
            (host_name, port) = proxy_string.rsplit(':', 1)
            host_name = host_name.split('://')[-1]
            
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(host_name)
            proxy.setPort(int(port))
            QNetworkProxy.setApplicationProxy(proxy)
        
        # Visit authorize url and get redirected url.
        plugin_class = plugin.plugins[service].Plugin
        url = plugin_class.getAuthorize()
        callback = plugin_class.getCallbackUrl()
        log.debug(url)
        web = WebView(url, callback)
        web.exec()
        
        # Visit access token url.
        url, data, headers = plugin_class.getAccessToken(web.getRedirectedUrl())
        opener = urllib.request.FancyURLopener(global_proxy)
        for k,v in headers.items():
            opener.addheader(k, v)
        f = opener.open(url, data)
        data = f.read().decode('utf-8')
        
        # Parse returned data.
        access_token, access_token_secret = plugin_class.parseData(data)
        account_manager.addAccount(service, '', '', access_token, access_token_secret, config_manager.getParameter('Proxy'))
        pass