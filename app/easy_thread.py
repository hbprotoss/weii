# coding=utf-8

'''
Module for easily creating new thread to run custom function and invoke callback function after done.
Specially used when GUI thread wants to do time-consuming task but doesn't want to block GUI.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import logger

log = logger.getLogger(__name__) 

SIGNAL_TASK_FINISH = SIGNAL('taskFinished')
class Task(QObject):
    def __init__(self, func, args=(), kwargs={}, callback=None, parent=None):
        super(Task, self).__init__(parent)
        
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.callback = callback
        # Parent thread object, for __init__ is called within parent thread context.
        self.parent_thread = QThread.currentThread()
        
    def run(self):
        args = self.func(*self.args, **self.kwargs)
        self.emit(SIGNAL_TASK_FINISH, self, args)
        
# Dict to maintain reference to QThread object in case of deleted by Python gc.
thread_dict = dict()

def start(func, args=(), kwargs={}, callback=None):
    '''
    @param func: callable object to be invoked by the run() method.
                 Must return a tuple and a dict as the parameters passed to callback function.
    @param args: the argument tuple for the target invocation. Defaults to ().
    @param kwargs: a dictionary of keyword arguments for the target invocation. Defaults to {}.
    @param callback: callable object to be invoked after func() is done.
    '''
    task = Task(func, args, kwargs, callback)
    thread = QThread()
    thread_dict[task] = thread
    task.moveToThread(thread)
    
    QObject.connect(thread, SIGNAL('started()'), task.run)
    QObject.connect(task, SIGNAL_TASK_FINISH, thread.quit)
    QObject.connect(task, SIGNAL_TASK_FINISH, onFinished)
    #QObject.connect(thread, SIGNAL('finished()'), thread.deleteLater)
    
    thread.start()
    
def onFinished(task, args):
    # This function is invoked within parent thread context
    if task.callback:
        task.callback(*args)
    thread_dict[task].wait()
    del thread_dict[task]
    task.deleteLater()