#!/usr/bin/env python3

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class StackedWidget(QWidget):
    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)
        self.scroll_pos = {}
        self.current_widget = None
        self.widgets = set()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
    def addWidget(self, w):
        self.widgets.add(w)
        self.layout.addWidget(w)
        self.current_widget = w
        self.showCurrentWidget()
        self.scroll_pos[w] = 0
        
    def currentWidget(self):
        return self.current_widget
    
    def setCurrentWidget(self, w):
        self.current_widget = w
        self.showCurrentWidget()
        
    def showCurrentWidget(self):
        if self.count() > 0:
            for widget in self.widgets:
                widget.hide()
            self.current_widget.show()
            self.updateGeometry()
            
    def sizeHint(self):
        if self.count() > 0:
            return self.current_widget.minimumSizeHint()
        else:
            return QWidget.sizeHint(self)
        
    def setScrollPosition(self, w, pos):
        self.scroll_pos[w] = pos
        
    def getScrollPosition(self, w):
        return self.scroll_pos[w]
    
    def count(self):
        return len(self.widgets)
        