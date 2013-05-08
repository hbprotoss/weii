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

# Image resources
TRAY_ICON = os.path.join(APP_ROOT, 'theme/logo.png')
ALL_ACCOUNTS = os.path.join(APP_ROOT, 'theme/all.png')
APP_LOGO = os.path.join(APP_ROOT, 'theme/logo.png')
ALL_ACCOUNTS_AVATAR = os.path.join(APP_ROOT, 'theme/all_accounts_avatar.png')
BROKEN_AVATAR = os.path.join(APP_ROOT, 'theme/broken_avatar.png')
BROKEN_IMAGE = os.path.join(APP_ROOT, 'theme/broken_image.png')
BUBLE = os.path.join(APP_ROOT, 'theme/buble.png')

# Configuration
DATABASE = os.path.join(DATA_ROOT, 'db.sqlite')
GLOBAL_CONFIG = os.path.join(DATA_ROOT, 'conf.ini')
KEYWORDS_FILE = os.path.join(DATA_ROOT, 'keywords.txt')