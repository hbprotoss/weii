#!/usr/bin/env python3

import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app.widget import picture_viewer

class FakeManager:
    def get(self, url, func):
        return '/home/digimon/123.jpg'

app = QApplication(sys.argv)

instance = picture_viewer.PictureViewer('', FakeManager())
instance.show()

app.exec() 