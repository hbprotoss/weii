#!/usr/bin/env python3

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app.widget import icon_button

class Test(QDialog):
    def __init__(self):
        super(Test, self).__init__()
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        
        self.edit = QLineEdit()
        hbox.addWidget(self.edit)
        
        self.btn = icon_button.IconButton()
        self.btn.loadIcon('/home/digimon/Desktop/Projects/weibo/app/theme/default/icon/home.png')
        hbox.addWidget(self.btn)
        
        self.connect(self.btn, SIGNAL('clicked()'), lambda :self.btn.setBuble(int(self.edit.text())))

app = QApplication(sys.argv)

t = Test()
t.show()

app.exec()