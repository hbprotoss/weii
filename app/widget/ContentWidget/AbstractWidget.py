# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AbstractWidget(QWidget):
    '''
    Abstract widget for holding content
    '''
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.__layout = QVBoxLayout()
        self.__layout.setMargin(0)
        self.__layout.addStretch()
        self.setLayout(self.__layout)
        #self.refresh([])
        
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