# coding=utf-8

import imghdr

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app import theme_manager
from app import logger
from app import constant

SIGNAL_FINISH = SIGNAL('downloadFinished')
SIGNAL_PROGRESS = SIGNAL('progress')
SIGNAL_ZOOM = SIGNAL('zoom')

log = logger.getLogger(__name__)

class DownloadTask(QThread):
    def __init__(self, url, manager, parent=None):
        super(DownloadTask, self).__init__(parent)
        log.debug('Start downloading %s' % url)
        self.url = url
        self.manager = manager
        
    def reportHook(self, transferred_blocks, bytes_per_block, total_size):
        percentage = int(transferred_blocks * bytes_per_block / total_size * 100)
        #log.debug('%d%% completed' % percentage)
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
        
class ScrollArea(QScrollArea):
    def __init__(self, *argv, **kwargv):
        super(ScrollArea, self).__init__(*argv, **kwargv)
        self.zoom_delta = 0.1
        self.ratio = 1.0
        self.original_size = None
        self.image = None
        self.last_pos = None            # Last mouse position when left button down 
        self.cursor_magnify = QCursor(QPixmap(constant.CURSOR_MAGNIFY))
        
        self.left_button_down = False
        self.ctrl_down = False
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setSingleStep(1)
        self.horizontalScrollBar().setSingleStep(1)
        
    def setWidget(self, w):
        super(ScrollArea, self).setWidget(w)
        if not isinstance(w, QLabel):
            return
        
        if w.movie():
            self.image = QMovie(w.movie())
            rect = self.image.frameRect()
            self.original_size = QSize(rect.width(), rect.height())
        else:
            self.image = QPixmap(w.pixmap())
            self.original_size = self.image.size()
            
    def wheelEvent(self, ev):
        if not self.ctrl_down:
            if ev.delta() > 0:
                direction = 1
            else:
                direction = -1
            v = self.verticalScrollBar()
            v.setValue(v.value() - direction * 80)      # Opposite to slider direction
            return
        
        widget = self.widget()
        if isinstance(widget, LoadingIndicator):
            return
        
        if ev.delta() > 0:
            self.ratio += self.zoom_delta
            if self.ratio > 2.0:
                self.ratio = 2.0
        else:
            self.ratio -= self.zoom_delta
            if self.ratio < 0.2:
                self.ratio = 0.2
                
        width = self.original_size.width() * self.ratio
        height = self.original_size.height() * self.ratio
        
        if widget.movie():
            pic = QMovie(self.image)
            pic.setScaledSize(QSize(width, height))
            widget.setMovie(pic)
        else:
            pic = self.image.scaled(QSize(width, height), transformMode=Qt.SmoothTransformation)
            widget.setPixmap(pic)
        widget.resize(QSize(width, height))
        
        self.emit(SIGNAL_ZOOM, self.ratio)
        
    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.last_pos = ev.globalPos()
            self.left_button_down = True
        else:
            self.left_button_down = False
            
    def mouseReleaseEvent(self, ev):
        self.left_button_down = False
        
    def mouseMoveEvent(self, ev):
        if not self.left_button_down:
            return
        pos = ev.globalPos()
        delta_x = pos.x() - self.last_pos.x()
        delta_y = pos.y() - self.last_pos.y()
        #log.debug('%d %d' % (delta_x, delta_y))
        
        v = self.verticalScrollBar()
        v.setValue(v.value() - delta_y)     # Opposite to slider direction
        h = self.horizontalScrollBar()
        h.setValue(h.value() - delta_x)     # Opposite to slider direction
        
        self.last_pos = pos
        
    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Control:
            self.setCursor(self.cursor_magnify)
            self.ctrl_down = True
            
    def keyReleaseEvent(self, ev):
        if ev.key() == Qt.Key_Control:
            self.setCursor(Qt.ArrowCursor)
            self.ctrl_down = False

class PictureViewer(QDialog):
    def __init__(self, url, manager, parent=None):
        '''
        @param url: string. URL of picture to be retrieved.
        @param manager: RecourseManager.
        '''
        super(PictureViewer, self).__init__(parent)
        
        self.title = url.rsplit('/', 1)[-1]
        
        self.setupUI()
        self.resize(400, 400)
        self.setWindowTitle('100%% %s' % self.title)
        self.setMouseTracking(True)
        #self.setStyleSheet('border-style: solid; border-width: 5px')
        
        self.task = DownloadTask(url, manager)
        self.connect(self.task, SIGNAL_PROGRESS, self.updateProgress)
        self.connect(self.task, SIGNAL_FINISH, self.updateUI)
        self.task.start()
        
        self.connect(self.scroll_area, SIGNAL_ZOOM, self.onZoom)
        
    def closeEvent(self, ev):
        self.task.terminate()
        self.close()
        
    def updateProgress(self, percentage):
        self.indicator.setPercentage(percentage)
        
    def updateUI(self, path):
        '''
        Replace the progress indicator with downloaded image
        @param path: string. Downloaded image path
        '''
        self.indicator.hide()
        self.scroll_area.takeWidget()
        
        label_pic = QLabel()
        self.image_type = imghdr.what(path)
        if self.image_type == 'gif':
            self.image = QMovie(path)
            self.image.start()
            label_pic.setMovie(self.image)
            rect = self.image.frameRect()
            self.original_size = QSize(rect.width(), rect.height())
        else:
            self.image = QPixmap(path, self.image_type)
            label_pic.setPixmap(self.image)
            self.original_size = self.image.size()
        self.scroll_area.setWidget(label_pic)
        
        self.resize(self.original_size)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)
        
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.scroll_area)
        
        self.indicator = LoadingIndicator()
        self.scroll_area.setWidget(self.indicator)
        
    def onZoom(self, ratio):
        self.setWindowTitle('%d%% %s' % (int(ratio * 100), self.title))