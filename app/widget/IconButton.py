#coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class IconButton(QToolButton):
    '''
    Button holding icon
    '''
    
    def __init__(self, parent=None):
        super(IconButton, self).__init__(parent)
        #self.setMinimumSize(35, 35)
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        
    def loadIcon(self, icon_file_name):
        icon = QIcon()
        icon.addFile(icon_file_name, QSize(32, 32))
        self.setIcon(icon)
        self.setIconSize(QSize(32, 32))