#coding=utf-8

import os

######################################################################
# Tweet type. The alternative value of key 'type' in Tweet object.
COMMENT = 0
TWEET = 1
######################################################################

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.expanduser('~/.weibo')

AVATER_SIZE = 64
AVATER_IN_TWEET_SIZE = 40

TRAY_ICON = os.path.join(APP_ROOT, 'theme/logo.png')
APP_LOGO = os.path.join(APP_ROOT, 'theme/logo.png')
DEFAULT_AVATER = os.path.join(APP_ROOT, 'theme/user_logo_64x64.png')
BUBLE = os.path.join(APP_ROOT, 'theme/buble.png')
DATABASE = os.path.join(DATA_ROOT, 'db.sqlite')

GLOBAL_CONFIG = os.path.join(DATA_ROOT, 'conf.ini')