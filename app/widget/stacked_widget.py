#!/usr/bin/env python3

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class StackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)
        self.scroll_pos = {}
        
    def addWidget(self, w):
        super(StackedWidget, self).addWidget(w)
        self.scroll_pos[w] = 0
        
    def setScrollPosition(self, w, pos):
        self.scroll_pos[w] = pos
        
    def getScrollPosition(self, w):
        return self.scroll_pos[w]
        
    def setCurrentWidget(self, widget):
        # Automatically switch size depending on the content of the page
        # @see: http://doc.qt.digia.com/qq/qq06-qwidgetstack.html
        # TODO: remember scroll position of last widget
        self.currentWidget().setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        super(StackedWidget, self).setCurrentWidget(widget)
        self.currentWidget().setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)