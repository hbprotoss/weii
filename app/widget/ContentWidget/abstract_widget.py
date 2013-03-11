# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app import constant
from app import theme_manager

class AbstractWidget(QWidget):
    '''
    Abstract widget for holding content
    '''
    
    def __init__(self, parent=None):
        super(AbstractWidget, self).__init__(parent)
        self.theme_manager= theme_manager.getCurrentTheme()
        
        self.loading_image = QMovie(theme_manager.getParameter('Skin', 'loading-image'))
        self.loading_image.start()
        
        self.small_loading_image = QMovie(theme_manager.getParameter('Skin', 'loading-image'))
        self.small_loading_image.setScaledSize(QSize(constant.AVATER_IN_TWEET_SIZE, constant.AVATER_IN_TWEET_SIZE))
        self.small_loading_image.start()
        
        image = QMovie(theme_manager.getParameter('Skin', 'loading-image'))
        image.setScaledSize(QSize(32, 32))
        image.start()
        self.refreshing_image = QLabel()
        self.refreshing_image.setMovie(image)
        self.refreshing_image.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
#        self.refreshing_image.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#        self.refreshing_image.setFixedSize(32, 32)
        
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
    
    def refresh(self):
        '''
        Refresh self with data from account list
        @param account_list: List of account objects(Plugin)
        '''
        raise NotImplementedError
