#!/usr/bin/env python3

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app.widget import picture_viewer

app = QApplication(sys.argv)

instance = picture_viewer.PictureViewer('')
instance.show()

app.exec() 