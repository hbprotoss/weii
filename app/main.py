#!/usr/bin/env python3

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *


path = os.path.dirname(os.path.realpath(__file__))
path = os.path.abspath(os.path.join(path, '../'))
sys.path.append(path)
os.chdir(path)

from app import constant
if not os.path.exists(constant.DATA_ROOT):
    os.mkdir(constant.DATA_ROOT)

import widget.main_window

app = QApplication(sys.argv)
instance = widget.main_window.MainWindow()
instance.show()
app.exec()
