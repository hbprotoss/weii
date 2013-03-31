#coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import constant

image_buble = QImage(constant.BUBLE)

class IconButton(QToolButton):
    '''
    Button holding icon
    '''
    
    def __init__(self, parent=None):
        super(IconButton, self).__init__(parent)
        self.unread_count = 0
        
    def loadIcon(self, icon_file_name):
        icon = QIcon()
        icon.addFile(icon_file_name, QSize(32, 32))
        self.setIcon(icon)
        self.setIconSize(QSize(32, 32))
        
    def setBuble(self, count):
        '''
        @param count: int. Unread message count.
        '''
        self.unread_count = count
        self.repaint()
        
    def paintEvent(self, ev):
        super(IconButton, self).paintEvent(ev)
        
        if self.unread_count:
            buble_width = image_buble.width()
            x = self.width() - buble_width
            
            painter = QPainter(self)
            painter.drawImage(x, 0, image_buble)
            painter.setPen(QColor(255, 255, 255))
            
            font = QFont()
            font.setPointSize(8 if self.unread_count < 10 else 7)
            painter.setFont(font)
            
            if self.unread_count >= 100:
                text = '...'
            else:
                text = str(self.unread_count)
            painter.drawText(QRectF(x, 0, buble_width, buble_width), text, QTextOption(Qt.AlignCenter))