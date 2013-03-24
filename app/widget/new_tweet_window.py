# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import account_manager

class NewTweetWindow(QDialog):
    '''
    Post new tweet
    '''
    def __init__(self, parent=None):
        super(NewTweetWindow, self).__init__(parent)
        self.setMinimumSize(400, 200)
        
        self.setupUI()
        
    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        self.editor = QTextEdit()
        #self.editor.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        vbox.addWidget(self.editor)
        
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        self.account_bar = QHBoxLayout()
        hbox.addLayout(self.account_bar)
        hbox.addStretch()
        self.btn_send = QPushButton('发送')
        hbox.addWidget(self.btn_send)