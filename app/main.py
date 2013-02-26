#!/usr/bin/env python3

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

path = os.path.dirname(os.path.abspath(__file__))
path = os.path.abspath(os.path.join(path, '../'))
sys.path.append(path)
os.chdir(path)

import widget.MainWindow


app = QApplication(sys.argv)
instance = widget.MainWindow.MainWindow()
instance.show()
app.exec()