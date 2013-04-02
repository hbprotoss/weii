# coding=utf-8

import urllib.parse

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from app import account_manager, theme_manager
from app import logger

SIGNAL_SELECTED = SIGNAL('selected')
SIGNAL_UNSELECTED = SIGNAL('unselected')

log = logger.getLogger(__name__)

class PicButton(QLabel):
    '''
    Signal:
        clicked(): Button is clicked(the same as QPushbutton)
    '''
    def __init__(self, image=None, parent=None):
        '''
        @param image: QImage. Original image
        '''
        super(PicButton, self).__init__(parent)
        
        self.setCursor(Qt.PointingHandCursor)
        if image:
            self.setPixmap(QPixmap.fromImage(image))
            
    def mouseReleaseEvent(self, ev):
        self.emit(SIGNAL('clicked()'))

class AccountButton(QLabel):
    '''
    A button with two states: activated(display original image) and deactivated(greyscaled image)
    '''
    def __init__(self, account, parent=None):
        super(AccountButton, self).__init__(parent)
        self.account = account
        self.enabled = account.if_send
        
        self.pixmaps = [
            # Greyscaled logo
            QPixmap.fromImage(self.convertToGreyscale(account.service_icon)),
            # Original logo
            QPixmap.fromImage(account.service_icon)
        ]
        
        self.setPixmap(self.pixmaps[int(self.enabled)])
        self.setCursor(Qt.PointingHandCursor)
        
    def convertToGreyscale(self, image):
        '''
        @param image: QImage. Original image
        @return: QImage. Greyscaled image
        '''
        rtn = QImage(image)
        for i in range(rtn.width()):
            for j in range(rtn.height()):
                grey = qGray(image.pixel(i, j))
                rtn.setPixel(QPoint(i, j), qRgb(grey, grey, grey))
        return rtn
        
    def mouseReleaseEvent(self, ev):
        self.enabled = not self.enabled
        self.setPixmap(self.pixmaps[int(self.enabled)])
        if self.enabled:
            self.emit(SIGNAL_SELECTED, self.account)
        else:
            self.emit(SIGNAL_UNSELECTED, self.account)
        
SIGNAL_FINISH = SIGNAL('TaskFinished')
class Task(QThread):
    def __init__(self, accounts, text, pic=None, parent=None):
        '''
        @param text: string. Original text.
        @param pic: file object. Opened file object of picture.
        '''
        super(Task, self).__init__(parent)
        self.text = text
        self.pic = pic
        self.accounts = accounts
    
    def run(self):
        rtn = {}
        try:
            for account in self.accounts:
                rtn = account.plugin.sendTweet(self.text, self.pic)
                log.debug(rtn)
        except urllib.error.HTTPError as e:
            log.error(e)
        finally:
            self.emit(SIGNAL_FINISH, rtn)

class NewTweetWindow(QDialog):
    '''
    Post new tweet
    '''
    def __init__(self, parent=None):
        super(NewTweetWindow, self).__init__(parent)
        self.pic_file = None
        self.selected_accounts = set()

        self.setWindowTitle('发布新微博')
        self.setMinimumSize(400, 200)
        self.setupUI()
        self.renderUI()
        
        self.connect(self.btn_send, SIGNAL('clicked()'), self.onClicked_BtnSend)
        self.connect(self.btn_upload_pic, SIGNAL('clicked()'), self.onClicked_UploadPic)
        
    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)
        
        hbox1 = QHBoxLayout()
        vbox.addLayout(hbox1)
        
        self.thumbnail = QLabel()
        thumbnail_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        thumbnail_policy.setHorizontalStretch(1)
        self.thumbnail.setSizePolicy(thumbnail_policy)
        hbox1.addWidget(self.thumbnail)
        
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        editor_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        editor_policy.setHorizontalStretch(4)
        self.editor.setSizePolicy(editor_policy)
        hbox1.addWidget(self.editor)
        
        hbox2 = QHBoxLayout()
        vbox.addLayout(hbox2)
        
        self.account_bar = QHBoxLayout()
        hbox2.addLayout(self.account_bar)
        for account in account_manager.getAllAccount():
            account_button = AccountButton(account)
            self.account_bar.addWidget(account_button)
            if account.if_send:
                self.selectAccount(account)
            # Receive signal
            self.connect(account_button, SIGNAL_SELECTED, self.selectAccount)
            self.connect(account_button, SIGNAL_UNSELECTED, self.unselectAccount)
                
        self.account_bar.addWidget(QLabel('|'))
        self.btn_upload_pic = PicButton()
        self.account_bar.addWidget(self.btn_upload_pic)
            
        hbox2.addStretch()
        self.btn_send = QPushButton('发送')
        hbox2.addWidget(self.btn_send)
        
    def renderUI(self):
        self.btn_upload_pic.setPixmap(QPixmap(theme_manager.getParameter(theme_manager.SKIN, 'upload-pic')))
        self.thumbnail.hide()
    
    def updateUI(self, tweet_object):
        self.btn_send.setEnabled(True)
        self.btn_send.setText('发送')
        self.editor.clear()
        self.close()
        
    def selectAccount(self, account):
        self.selected_accounts.add(account)
        
    def unselectAccount(self, account):
        self.selected_accounts.remove(account)
        
    def getSelectedAccounts(self):
        return list(self.selected_accounts)
    
    def onClicked_BtnSend(self):
        text = self.editor.toPlainText()
        if text:
            log.debug(text)
            
            accounts = self.getSelectedAccounts()
            if len(accounts) > 0:
                self.btn_send.setText('发送中...')
                self.btn_send.setEnabled(False)
        
                self.task = Task(accounts, text, self.pic_file)
                self.task.start()
                self.connect(self.task, SIGNAL_FINISH, self.updateUI)
            else:
                # TODO: No account selected
                QMessageBox.critical(self, '错误', '请至少选择一个账户!')
        else:
            QMessageBox.critical(self, '错误', '微博不能为空!')
        
    def onClicked_UploadPic(self):
        dlg = QFileDialog(self, '选择图片')
        dlg.setNameFilter('Image Files(*.png *.jpg *.jpeg *.gif)')
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setOption(QFileDialog.DontUseNativeDialog)
        if not dlg.exec():
            self.pic_file = None
        else:
            self.pic_file = dlg.selectedFiles()[0]
            log.debug(self.pic_file)
            
            height = self.editor.height()
            self.thumbnail.show()
            self.thumbnail.setPixmap(QPixmap(self.pic_file).scaled(100, height, Qt.KeepAspectRatio))
