#!/usr/bin/env python3

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class StackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super(StackedWidget, self).__init__(parent)
        
    def setCurrentWidget(self, widget):
        # Automatically switch size depending on the content of the page
        # @see: http://doc.qt.digia.com/qq/qq06-qwidgetstack.html
        self.currentWidget().setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        super(StackedWidget, self).setCurrentWidget(widget)
        self.currentWidget().setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)