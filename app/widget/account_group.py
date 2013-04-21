# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

SIGNAL_SELECTED = SIGNAL('selected')
SIGNAL_UNSELECTED = SIGNAL('unselected')

class AccountButton(QLabel):
    '''
    A button with two states: activated(display original image) and deactivated(greyscaled image)
    '''
    def __init__(self, account, parent=None):
        super(AccountButton, self).__init__(parent)
        self.account = account
        self.enabled = account.if_send
        
        self.pixmaps = [
            # Greyscaled logo
            QPixmap.fromImage(self.convertToGreyscale(account.service_icon)),
            # Original logo
            QPixmap.fromImage(account.service_icon)
        ]
        
        self.setPixmap(self.pixmaps[int(self.enabled)])
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self.account.plugin.username)
        
    def convertToGreyscale(self, image):
        '''
        @param image: QImage. Original image
        @return: QImage. Greyscaled image
        '''
        rtn = QImage(image)
        for i in range(rtn.width()):
            for j in range(rtn.height()):
                grey = qGray(image.pixel(i, j))
                rtn.setPixel(QPoint(i, j), qRgb(grey, grey, grey))
        return rtn
        
    def mouseReleaseEvent(self, ev):
        self.enabled = not self.enabled
        self.setPixmap(self.pixmaps[int(self.enabled)])
        if self.enabled:
            self.emit(SIGNAL_SELECTED, self.account)
        else:
            self.emit(SIGNAL_UNSELECTED, self.account)
