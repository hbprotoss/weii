#coding=utf-8

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.expanduser('~/.weibo')

AVATER_SIZE = 64
AVATER_IN_TWEET_SIZE = 40

DEFAULT_AVATER = os.path.join(APP_ROOT, 'theme/user_logo_64x64.png')
BUBLE = os.path.join(APP_ROOT, 'theme/buble.png')
DATABASE = os.path.join(DATA_ROOT, 'db.sqlite')

GLOBAL_CONFIG = os.path.join(DATA_ROOT, 'conf.ini')