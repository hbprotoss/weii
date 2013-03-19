#!/usr/bin/env python3

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app.widget import setting_window

app = QApplication(sys.argv)

instance = setting_window.SettingWindow()
instance.show()

app.exec()