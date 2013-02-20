# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AbstractWidget(QWidget):
    '''
    Abstract widget for holding content
    '''
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self._layout = QVBoxLayout()
        self._layout.setMargin(0)
        self._layout.addStretch()
        self.setLayout(self._layout)
        #self.refresh([])
        
    def insertWidget(self, pos, widget):
        '''
        @param pos: Insert at pos
        @param widget: Widget to be added
        '''
        self._layout.insertWidget(pos, widget)
    
    def refresh(self, account_list):
        '''
        Refresh self with data from account list
        @param account_list: List of account objects(Plugin)
        '''
        raise NotImplementedError