#!/usr/bin/env python3

import sys
import os
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *


path = os.path.dirname(os.path.abspath(__file__))
path = os.path.abspath(os.path.join(path, '../'))
sys.path.append(path)
os.chdir(path)

from app import constant
if not os.path.exists(constant.DATA_ROOT):
    os.mkdir(constant.DATA_ROOT)

import widget.main_window

os.environ['TZ'] = 'Asia/Shanghai'
time.tzset()

app = QApplication(sys.argv)
instance = widget.main_window.MainWindow()
instance.show()
app.exec()
