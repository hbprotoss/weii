#coding=utf-8

import configparser
from PyQt4.QtCore import QThread

# Global variable
main_window = None

class ConfParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr
    
class ThreadProc(QThread):
    def __init__(self, task, argvs, callback=None, parent=None):
        '''
        Start a new thread to run the task procedure with argvs. When the task is finished, call the
        callback procedure with arguments returned by task.
        @param task: callable object. def task(*argvs), return tuple
        @param argvs: tuple. Arguments.
        @param callback: callable object. def callback(*argvs)
        '''
        super(ThreadProc, self).__init__(parent)
        self.task = task
        self.argvs = argvs
        self.callback = callback
        
    def run(self):
        rtn = self.task(*self.argvs)
        if self.callback:
            self.callback(*rtn)
        pass