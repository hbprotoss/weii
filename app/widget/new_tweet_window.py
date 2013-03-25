# coding=utf-8

import urllib.parse

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import account_manager
from app import logger

SIGNAL_CLICKED = SIGNAL('clicked')

log = logger.getLogger(__name__)

class AccountButton(QLabel):
    def __init__(self, account, parent=None):
        super(AccountButton, self).__init__(parent)
        self.account = account
        self.enabled = account.if_send
        
        self.pixmaps = [
            QPixmap.fromImage(self.convertToGreyscal(account.service_icon)),
            QPixmap.fromImage(account.service_icon)
        ]
        
        self.setPixmap(self.pixmaps[int(self.enabled)])
        #self.setPixmap(self.pixmaps[0])
        self.setCursor(Qt.PointingHandCursor)
        
    def convertToGreyscal(self, image):
        '''
        @param image: QImage. Original image
        @return: QImage. Greyscaled image
        '''
        # TODO: convert to greyscale image
        rtn = QImage(image)
        for i in range(rtn.width()):
            for j in range(rtn.height()):
                grey = qGray(image.pixel(i, j))
                rtn.setPixel(QPoint(i, j), qRgb(grey, grey, grey))
        return rtn
        
    def mouseReleaseEvent(self, ev):
        self.enabled = not self.enabled
        self.setPixmap(self.pixmaps[int(self.enabled)])
        self.emit(SIGNAL_CLICKED, self.account, self.enabled)

class NewTweetWindow(QDialog):
    '''
    Post new tweet
    '''
    def __init__(self, parent=None):
        super(NewTweetWindow, self).__init__(parent)
        self.setMinimumSize(400, 200)
        
        self.setupUI()
        self.renderUI()
        
        self.connect(self.btn_send, SIGNAL('clicked()'), self.onClicked_BtnSend)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        self.editor = QTextEdit()
        self.editor.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        #self.editor.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        vbox.addWidget(self.editor)
        
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        
        self.account_bar = QHBoxLayout()
        hbox.addLayout(self.account_bar)
        for account in account_manager.getAllAccount():
            account_button = AccountButton(account)
            self.account_bar.addWidget(account_button)
            
        hbox.addStretch()
        self.btn_send = QPushButton('发送')
        hbox.addWidget(self.btn_send)
        
    def renderUI(self):
        pass
    
    def onClicked_BtnSend(self):
        text = self.editor.toPlainText()
        log.debug(text)
        for account in account_manager.getAllAccount():
            if account.if_send:
                rtn = account.plugin.sendTweet(text)
                log.debug(rtn)