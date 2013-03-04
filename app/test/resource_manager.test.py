#/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath('../'))

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import resource_manager

class Test(QDialog):
    def __init__(self):
        super(Test, self).__init__()
        self.manager = resource_manager.ResourceManager('test', 'pic', {'https': 'http://127.0.0.1:10001'})
        
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        hbox = QHBoxLayout()
        self.edit = QLineEdit()
        hbox.addWidget(self.edit)
        self.button = QPushButton('fetch')
        hbox.addWidget(self.button)
        vbox.addLayout(hbox)
        
        self.image = QLabel()
        vbox.addWidget(self.image)
        
        self.connect(self.button, SIGNAL('clicked()'), self.clicked)
        
    def clicked(self):
        res = self.manager.get(self.edit.text())
        self.image.setPixmap(res)

app = QApplication(sys.argv)

t = Test()
t.show()

app.exec()