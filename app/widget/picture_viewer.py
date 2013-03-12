# coding=utf-8

import imghdr

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app import theme_manager
from app import logger

SIGNAL_FINISH = SIGNAL('downloadFinished')
SIGNAL_PROGRESS = SIGNAL('progress')

log = logger.getLogger(__name__)

class DownloadTask(QThread):
    def __init__(self, url, manager, parent=None):
        super(DownloadTask, self).__init__(parent)
        log.debug(url)
        self.url = url
        self.manager = manager
        
    def reportHook(self, transferred_blocks, bytes_per_block, total_size):
        percentage = int(transferred_blocks * bytes_per_block / total_size * 100)
        log.debug('%d%% completed' % percentage)
        self.emit(SIGNAL_PROGRESS, percentage)
        
    def run(self):
        path = self.manager.get(self.url, self.reportHook)
        log.debug('%s finished' % self.url)
        log.debug('save to %s' % path)
        self.emit(SIGNAL_FINISH, path)

class LoadingIndicator(QWidget):
    '''
    Composed of a loading animater and a percentage indicator
    '''
    
    def __init__(self, parent=None):
        super(LoadingIndicator, self).__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        self.setLayout(vbox)
        
        gif = QMovie(theme_manager.getParameter('Skin', 'loading-image'))
        gif.start()
        label_loading = QLabel()
        label_loading.setMovie(gif)
        vbox.addWidget(label_loading)
        
        self.label_percentage = QLabel('0 %')
        self.label_percentage.setAlignment(Qt.AlignCenter)
        self.label_percentage.setStyleSheet('font-size: 20px')
        vbox.addWidget(self.label_percentage)
        
    def setPercentage(self, percentage):
        self.label_percentage.setText('%d %%' % int(percentage))

class PictureViewer(QDialog):
    def __init__(self, url, manager, parent=None):
        '''
        @param url: string. URL of picture to be retrieved.
        @param manager: RecourseManager.
        '''
        super(PictureViewer, self).__init__(parent)
        
        self.setupUI()
        self.resize(400, 400)
        self.setWindowTitle(url.rsplit('/', 1)[-1])
        #self.setStyleSheet('border-style: solid; border-width: 5px')
        
        self.task = DownloadTask(url, manager)
        self.connect(self.task, SIGNAL_PROGRESS, self.updateProgress)
        self.connect(self.task, SIGNAL_FINISH, self.updateUI)
        self.task.start()
        
    def updateProgress(self, percentage):
        self.indicator.setPercentage(percentage)
        
    def updateUI(self, path):
        self.indicator.hide()
        self.vbox.removeWidget(self.indicator)
        
        image = QPixmap(path, imghdr.what(path))
        label_pic = QLabel()
        label_pic.setPixmap(image)
        self.vbox.addWidget(label_pic)
        
        size = image.size()
        self.resize(size)
        
    def setupUI(self):
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignCenter)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)
        
        self.indicator = LoadingIndicator()
        self.vbox.addWidget(self.indicator)