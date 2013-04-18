#!/usr/bin/env python3

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

sys.path.append(os.path.realpath(os.path.join(os.path.realpath(__file__), '../../')))
from app.widget import *


app = QApplication(sys.argv)

instance = new_tweet_window.NewTweetWindow()
instance.show()

app.exec()