# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AbstractWidget(QWidget):
    '''
    Abstract widget for holding content
    '''
    
    def __init__(self, theme, parent=None):
        super(AbstractWidget, self).__init__(parent)
        self.theme= theme
        
        frame_layout = QVBoxLayout()
        frame_layout.setMargin(0)
        self.__layout = QVBoxLayout()
        self.__layout.setMargin(0)
        self.__layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        frame_layout.addLayout(self.__layout)
        frame_layout.addStretch()
        self.setLayout(frame_layout)
        
    def count(self):
        return self.__layout.count()
        
    def clearWidget(self, widget):
        widget.hide()
        self.__layout.removeWidget(widget)
        
    def clearAllWidgets(self):
        while(True):
            child = self.__layout.itemAt(0)
            if child:
                self.clearWidget(child.widget())
                del child
            else:
                break
        
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
