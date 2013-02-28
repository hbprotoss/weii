# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AbstractWidget(QWidget):
    '''
    Abstract widget for holding content
    '''
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        frame_layout = QVBoxLayout()
        frame_layout.setMargin(0)
        self.__layout = QVBoxLayout()
        self.__layout.setMargin(0)
        self.__layout.setAlignment(Qt.AlignTop)
        frame_layout.addLayout(self.__layout)
        frame_layout.addStretch()
        self.setLayout(frame_layout)
        
    def insertWidget(self, pos, widget):
        '''
        @param pos: Insert at pos
        @param widget: Widget to be added
        '''
        self.__layout.insertWidget(pos, widget)
        
    def addWidget(self, widget):
        '''
        @param widget: Widget to be added
        '''
        self.__layout.addWidget(widget)
    
    def refresh(self, account_list):
        '''
        Refresh self with data from account list
        @param account_list: List of account objects(Plugin)
        '''
        raise NotImplementedError