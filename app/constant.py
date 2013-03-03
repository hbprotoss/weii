#coding=utf-8

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.expanduser('~/.weibo')

AVATER_SIZE = 64

DEFAULT_AVATER = os.path.join(APP_ROOT, 'theme/user_logo_64x64.png')
TEST_SERVICE = os.path.join(APP_ROOT, '16x16.jpg')