#!/usr/bin/env python3

import sys
import os
import argparse
from PyQt4.QtCore import *
from PyQt4.QtGui import *

path = os.path.dirname(os.path.realpath(__file__))
path = os.path.abspath(os.path.join(path, '../'))
sys.path.append(path)
os.chdir(path)

from app import constant
from app import misc
if not os.path.exists(constant.DATA_ROOT):
    os.mkdir(constant.DATA_ROOT)

# Parse command line arguments
parser = argparse.ArgumentParser(description='weii SNS client platform')
parser.add_argument('-l', '--log', dest='log', default='INFO', help='Log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
options = parser.parse_args()

# Set global log level
from app import logger
logger.setLogLevel(options.log)

import widget.main_window

# Launching app
app = QApplication(sys.argv)

# Setting up main window
instance = widget.main_window.MainWindow()
instance.show()

misc.main_window = instance

app.exec()
