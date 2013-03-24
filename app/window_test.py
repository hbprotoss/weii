#!/usr/bin/env python3

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app.widget import *

app = QApplication(sys.argv)

instance = new_tweet_window.NewTweetWindow()
instance.show()

app.exec()