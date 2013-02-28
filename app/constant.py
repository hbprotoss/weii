#coding=utf-8

import os

MainWindow_QSS = '''
QDialog {
    background-color:%s;
    background-image:url(%s);
    background-repeat:no-repeat;
    padding: 5px
}
QToolButton {
    width:32 px; height:32 px;
    border-style: outset;
    border-radius: 5px;
}
QToolButton:hover {
    background-color:%s
}
QLabel#account {
    color: white;
    font-size: 16px;
    font-weight: bold;
}
QGroupBox {
    margin-top: 0px;
    padding-top: 0px;
    border-style: solid;
    border-width: 1px;
}
'''

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_AVATER = os.path.join(APP_ROOT, 'theme/user_logo_64x64.png')
TEST_SERVICE = os.path.join(APP_ROOT, '16x16.jpg')