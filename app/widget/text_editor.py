# coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

SIGNAL_READY_TO_SEND = SIGNAL('readyToSend')

class TextEditor(QTextEdit):
    def keyPressEvent(self, ev):
        if ev.modifiers() == Qt.ControlModifier and ev.key() == Qt.Key_Return:
            self.emit(SIGNAL_READY_TO_SEND)
        else:
            super(TextEditor, self).keyPressEvent(ev)