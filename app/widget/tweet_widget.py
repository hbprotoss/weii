#coding=utf-8

import imghdr
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from app import constant, theme_manager
from app import logger
from app import misc
from app import easy_thread
from app.widget import picture_viewer
from app.plugin import weiBaseException

log = logger.getLogger(__name__)

at_terminator = set(''' ~!@#$%^&*()+`={}|[]\;':",./<>?~！￥×（）、；：‘’“”《》？，。''')
url_legal = set('''!#$&'()*+,/:;=?@-._~'''
                + ''.join([chr(c) for c in range(ord('0'), ord('9')+1)])
                + ''.join([chr(c) for c in range(ord('a'), ord('z')+1)])
                + ''.join([chr(c) for c in range(ord('A'), ord('Z')+1)]))

SIGNAL_FINISH = SIGNAL('downloadFinished')
SIGNAL_THUMBNAIL_CLICKED = SIGNAL('thumbnailClicked')
SIGNAL_RESPONSE_CLICKED = SIGNAL('responseClicked')
SIGNAL_SUCCESSFUL_RESPONSE = SIGNAL('successfulResponse')

class Text(QLabel):
    def __init__(self, text, parent=None):
        super(Text, self).__init__(text, parent)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.TextSelectableByMouse)
        
class TweetText(Text):
    '''
    Widget holding tweet body
    '''
    def __init__(self, text, parent=None):
        super(TweetText, self).__init__(text, parent)
        self.setWordWrap(True)
        
    def resizeEvent(self, ev):
        #print(ev.oldSize().height(), ev.size().height(), self.heightForWidth(ev.oldSize().width()))
        #super(TweetText, self).resizeEvent(ev)
        self.setMaximumHeight(self.heightForWidth(ev.size().width()))
        
class PictureWidget(QLabel):
    '''
    Widget holding avatar and thumbnail
    '''
    
    def __init__(self, parent=None):
        super(PictureWidget, self).__init__(parent)
        
    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.emit(SIGNAL_THUMBNAIL_CLICKED)

class GroupBox(QGroupBox):
    def __init__(self, parent=None):
        super(GroupBox, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setStyleSheet(
            '''
            QGroupBox {
                margin-top: 0px;
                padding-top: 0px;
                border-style: outset;
                border-radius: 4px;
                border-width: 1px;
            }
            '''
        )
        
class TweetResponseButton(QLabel):
    '''
    Comment and repost button.
    The format is 'text(amount)' if amount greater than 0. 'text' if amount equals to 0.
    '''
    def __init__(self, text, amount=0, parent=None):
        super(TweetResponseButton, self).__init__(parent)
        self._text = text
        self._amount = amount
        
        self.setAmount(amount)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet('''
            color: blue;
        ''')
        
    def setAmount(self, amount):
        '''
        @param amount: int.
        '''
        self._amount = amount
        if amount:
            self.setText('%s(%d)' % (self._text, amount))
        else:
            self.setText(self._text)
            
    def increaseAmount(self):
        self.setAmount(self._amount + 1)
            
    def mouseReleaseEvent(self, ev):
        self.emit(SIGNAL_RESPONSE_CLICKED)

class ResponseWidget(QGroupBox):
    '''
    Widget for commenting or reposting a tweet.
    '''
    # Constant
    COMMENT = 0
    REPOST = 1
    
    def __init__(self, plugin, tweet, widget_type, parent=None):
        '''
        @param tweet: Tweet object.
        @param widget_type: COMMENT or REPOST. Determine whether comment or repost a tweet.
        '''
        super(ResponseWidget, self).__init__(parent)
        self.plugin = plugin
        self.tweet = tweet
        self.widget_type = widget_type
        
        self.setupUI()
        self.connect(self.button, SIGNAL('clicked()'), self.onClicked_Btn)
        self.setStyleSheet(
            '''
            QGroupBox {
                margin-top: 0px;
                padding: 5px;
                border-style: outset;
                border-radius: 4px;
                border-width: 1px;
            }
            '''
        )
        
    def setupUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(main_layout)
        
        self.edit = QTextEdit()
        self.edit.setMinimumHeight(27)
        self.edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        main_layout.addWidget(self.edit)
        
        hbox = QHBoxLayout()
        main_layout.addLayout(hbox)
        self.checkBox = QCheckBox('check box')
        hbox.addWidget(self.checkBox)
        
        hbox.addStretch()
        self.button = QPushButton('push')
        hbox.addWidget(self.button)
        
    def updateUI(self, tweet_object):
        self.button.setEnabled(True)
        self.edit.setEnabled(True)
        self.edit.clear()
        
        if 'error' not in tweet_object:
            # If successful, emit signal to notify TweetWidget to increase the
            # corresponding message counter.
            self.emit(SIGNAL_SUCCESSFUL_RESPONSE, self.widget_type)
        
    def procSendComment(self, original_tweet, text):
        tweet_type = original_tweet['type']
        try:
            if tweet_type == constant.TWEET:
                rtn = self.plugin.sendComment(original_tweet['id'], text)
            elif tweet_type == constant.COMMENT:
                rtn = self.plugin.sendRecomment(original_tweet['status']['id'], original_tweet['id'], text)
        except weiBaseException as e:
            rtn = {'error': str(e)}
        log.debug(rtn)
        return (rtn, ), {}
    
    def procSendRetweet(self, original_tweet, text):
        tid = original_tweet['id']
        try:
            rtn = self.plugin.sendRetweet(tid, text)
        except weiBaseException as e:
            rtn = {'error': str(e)}
        log.debug(rtn)
        return (rtn, ), {}
        
    def onClicked_Btn(self):
        text = self.edit.toPlainText()
        log.debug(text)
        self.button.setEnabled(False)
        self.edit.setEnabled(False)
        
        if self.widget_type == ResponseWidget.COMMENT:
            easy_thread.start(self.procSendComment,
                args=(self.tweet, text),
                callback=self.updateUI
            )
        elif self.widget_type == ResponseWidget.REPOST:
            if 'retweeted_status' in self.tweet:
                text = ''.join((text, '//@', self.tweet['user']['screen_name'], ': ', self.tweet['text']))
            easy_thread.start(self.procSendRetweet,
                args=(self.tweet, text),
                callback=self.updateUI
            )
        
    def setType(self, widget_type):
        '''
        @param widget_type: COMMENT or REPOST. Determine whether comment or repost a tweet.
        '''
        self.widget_type = widget_type
        if widget_type == ResponseWidget.COMMENT:
            self.checkBox.setText('同时转发')
            self.button.setText('评论')
        elif widget_type == ResponseWidget.REPOST:
            self.checkBox.setText('同时评论给 %s' % self.tweet['user']['screen_name'])
            self.button.setText('转发')
            
    def getType(self):
        return self.widget_type
        
class TweetWidget(QWidget):
    '''
    Widget for each tweet
    '''
    
    def __init__(self, account, tweet, avatar, thumbnail, parent=None):
        '''
        @param account: misc.Account object
        @param tweet: dict of tweet. See doc/插件接口设计.pdf: 单条微博
        @param avatar: QPixmap of user avatar
        @param thumbnail: QMovie showing that the thumbnail is still loading from Internet
        @return: None
        '''
        super(TweetWidget, self).__init__(parent)
        
        self.account = account
        self.tweet = tweet
        self.avatar = avatar
        self.thumbnail = thumbnail
        self.pic_url = ''
        self.time_format = '%Y-%m-%d %H:%M:%S'
        
        self.setupUI()
        self.renderUI()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        #self.setStyleSheet('border-style:solid;border-width:5px')
        
        self.connect(self.label_tweet, SIGNAL('linkActivated (const QString&)'), self.onLinkActivated)
        if self.label_retweet:
            self.connect(self.label_retweet, SIGNAL('linkActivated (const QString&)'), self.onLinkActivated)
        if self.label_thumbnail:
            self.connect(self.label_thumbnail, SIGNAL_THUMBNAIL_CLICKED, self.onClicked_Thumbnail)
            
        # Repost button
        self.connect(self.btn_tweet_repost, SIGNAL_RESPONSE_CLICKED, self.onClicked_Repost)
        # Comment button
        self.connect(self.btn_tweet_comment, SIGNAL_RESPONSE_CLICKED, self.onClicked_Comment)
        
        # Start downloading avatar
        avatar_url = tweet['user']['avatar_large']
        easy_thread.start(self.getResource,
            args=(avatar_url, self.account.avatar_manager, self.label_avatar,
                QSize(constant.AVATER_IN_TWEET_SIZE, constant.AVATER_IN_TWEET_SIZE)
            ),
            callback=self.updateUI
        )
        
        # Start downloading thumbnail if exists
        try:
            if 'thumbnail_pic' in tweet:
                url = tweet['thumbnail_pic']
            elif ('retweeted_status' in tweet) and ('thumbnail_pic' in tweet['retweeted_status']):
                url = tweet['retweeted_status']['thumbnail_pic']
            easy_thread.start(self.getResource,
                args=(url, self.account.picture_manager, self.label_thumbnail, None),
                callback=self.updateUI
            )
        except UnboundLocalError:
            # No picture
            pass
        
    def paintEvent(self, ev):
        super(TweetWidget, self).paintEvent(ev)
        size = self.size()
        painter = QPainter(self)
        color = 200
        painter.setPen(QColor(color, color, color))
        painter.drawLine(QPoint(5, size.height() - 1), QPoint(size.width() - 6, size.height() - 1))
        
    def getResource(self, url, manager, widget, size):
        pic_path = ''
        try:
            pic_path = manager.get(url)
        except Exception as e:
            log.error(e)
        finally:
            return (widget, pic_path, size), {}
        
    def onClicked_Repost(self):
        if self.response_widget.isHidden():
            self.response_widget.show()
        elif self.response_widget.getType() == ResponseWidget.REPOST:
            self.response_widget.hide()
        self.response_widget.setType(ResponseWidget.REPOST)
        
    def onClicked_Comment(self):
        if self.response_widget.isHidden():
            self.response_widget.show()
        elif self.response_widget.getType() == ResponseWidget.COMMENT:
            self.response_widget.hide()
        self.response_widget.setType(ResponseWidget.COMMENT)
        
    def onClicked_Thumbnail(self):
        #QMessageBox.information(self, 'test', self.pic_url)
        pic = picture_viewer.PictureViewer(self.pic_url, self.account.picture_manager, self)
        pic.setModal(False)
        
        main_window_rect = misc.main_window.geometry()
        #main_window_rect.left, main_window_rect.top = misc.main_window.mapToGobal(QPoint(0, 0))
        widget_rect = self.geometry()
        widget_rect.setTopLeft(self.mapToGlobal(QPoint(0, 0)))
        screen_rect = QApplication.desktop().availableGeometry()
        pic_size = pic.size()
        
        # Horizontal position
        if main_window_rect.right() + pic_size.width() > screen_rect.right():
            left = main_window_rect.left() - pic_size.width()
        else:
            left = main_window_rect.right()
        # Vertical position
        top = main_window_rect.top()
            
        pic.setGeometry(QRect(left, top, pic_size.width(), pic_size.height()))
        pic.show()
        
    def onLinkActivated(self, link):
        #log.debug(link)
        if link.startswith('http'):
            QDesktopServices.openUrl(QUrl(link))

    def findAtEnding(self, src, start):
        i = start
        length = len(src)
        while(i < length):
            if src[i] in at_terminator:
                return i
            i += 1
        return i
    
    def findUrlEnding(self, src, start):
        i = start
        length = len(src)
        while(i < length):
            if src[i] not in url_legal:
                return i
            i += 1
        return i
    
    def findEmotionEnding(self, src, start):
        i = start
        length = len(src)
        prefix_amount = 1       # In case of recursively having emotion expression.
        while(i < length):
            if src[i] == self.account.emotion_exp.prefix:
                prefix_amount += 1
            elif src[i] == self.account.emotion_exp.suffix:
                if prefix_amount == 1:
                    return i + 1
                else:
                    prefix_amount -= 1

            i += 1
        return i + 1
        
    def formatLink(self, src):
        if len(src) == 0:
            return src
        
        if src[0] == '@':
            rtn = '<a style="text-decoration:none" href="user:%s">%s</a>' % (src[1:], src)
        elif src[0] == 'h':
            rtn = '<a style="text-decoration:none" href="%s">%s</a>' % (src, src)
        elif src[0] == self.account.emotion_exp.prefix:
            try:
                emotion_path = self.account.emotion_manager.get(
                    self.account.emotion_dict[src]
                )
                rtn = '<img src="%s" />' % emotion_path
            except KeyError:
                # FIXME: [[xx], [xx] won't be analysed as emotion
                # Maybe emotion can't be found. Analyse the text between prefix and suffix.
                end = len(src) - 1 if src[len(src)-1] == self.account.emotion_exp.suffix else len(src)
                rtn = self.analyse(src[1 : end])
                end_chr = self.account.emotion_exp.suffix if src[len(src)-1] == self.account.emotion_exp.suffix else ''
                rtn = ''.join((src[0], rtn, end_chr))
        else:
            rtn = src
        return rtn
    
    def analyse(self, src):
        # FIXME: find a way to distinguish character and punctuation
        length = len(src)
        i = 0
        target = []
        try:
            while(i < length):
                # At
                if src[i] == '@':
                    end = self.findAtEnding(src, i+1)
                    target.append((i, end))
                    i = end
                # URL
                elif (src[i] == 'h' and src[i+1] == 't' and src[i+2] == 't' and src[i+3] == 'p'):
                    # http
                    if(src[i+4] == 's' and src[i+5] == ':' and src[i+6] == '/' and src[i+7] == '/'):
                        end = self.findUrlEnding(src, i+8)
                        target.append((i, end))
                        i = end
                    # https
                    elif(src[i+4] == ':' and src[i+5] == '/' and src[i+6] == '/'):
                        end = self.findUrlEnding(src, i+7)
                        target.append((i, end))
                        i = end
                # emotion
                elif src[i] == self.account.emotion_exp.prefix:
                    end = self.findEmotionEnding(src, i+1)
                    target.append((i, end))
                    i = end
                    pass
                else:
                    i += 1
        except IndexError:
            pass
        
        if(len(target) == 0):
            target.append((0, len(target)+1))
        
    #    for item in target:
    #        print(src[item[0] : item[1]])
            
        seg_list = []
        try:
            for index,item in enumerate(target):
                seg = src[item[0] : item[1]]
                seg = self.formatLink(seg)
                seg_list.append(seg)
                
                seg = src[ item[1] : target[index+1][0] ]
                seg = self.formatLink(seg)
                seg_list.append(seg)
            pass
        except IndexError:
            seg_list.append(src[ item[1] : ])
            pass
        
        rtn = ''.join(seg_list)
        if not (target[0][0] == 0):
            rtn = src[:target[0][0]] + rtn 
        return rtn

    def updateUI(self, widget, path, size=None):
        '''
        @param widget: QLabel. Widget to be updated
        @param path: string. Image path
        @param size: QSize. Actual size to be painted on the widget
        '''
        pic = QPixmap(path, imghdr.what(path))
        if(size):
            pic = pic.scaled(size, transformMode=Qt.SmoothTransformation)
        widget.setPixmap(pic)
        widget.setFixedSize(pic.size())
        
    def setThumbnail(self, path):
        self.label_thumbnail.setPixmap(QPixmap(path, imghdr.what(path)))
        
    def setupUI(self):
        hLayout = QHBoxLayout()
        hLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(hLayout)
        
        # avatar
        v1 = QVBoxLayout()
        hLayout.addLayout(v1)
        self.label_avatar = PictureWidget(self)
        self.label_avatar.setMovie(self.avatar)
        v1.addWidget(self.label_avatar)
        v1.addStretch()
        
        # tweet
        v2 = QVBoxLayout()
        hLayout.addLayout(v2)
        
        ## user, source, service
        h1 = QHBoxLayout()
        v2.addLayout(h1)
        label_user = Text(
            self.analyse('@' + str(self.tweet['user']['screen_name'])), self
        )
        #label_source = QLabel(self.tweet['source'])
        label_service_icon = QLabel(self)
        label_service_icon.setPixmap(QPixmap.fromImage(self.account.service_icon))
        h1.addWidget(label_user)
        #h1.addWidget(label_source)
        h1.addStretch()
        h1.addWidget(label_service_icon)
        
        ## tweet content
        #log.debug('Analysing %s' % self.tweet['text'])
        self.label_tweet = TweetText(
            self.analyse(self.tweet['text']), self
        )
        #log.debug('Done.')
        v2.addWidget(self.label_tweet)
        
        ## retweet if exists
        self.label_thumbnail = None
        self.label_retweet = None
        if('retweeted_status' in self.tweet):
            retweet = self.tweet['retweeted_status']
            
            groupbox = GroupBox(self)
            #groupbox.setContentsMargins(0, 5, 5, 5)
            v2.addWidget(groupbox)
            v3 = QVBoxLayout()
            v3.setContentsMargins(5, 5, 5, 5)
            groupbox.setLayout(v3)
            
            h3 = QHBoxLayout()
            v3.addLayout(h3)
            label_retweet_user = Text(
                self.analyse('@' + retweet['user']['screen_name']), self
            )
            #label_retweet_source = QLabel(retweet['source'])
            h3.addWidget(label_retweet_user)
            #h3.addWidget(label_retweet_source)
            h3.addStretch()
            
            self.label_retweet = TweetText(
                self.analyse(retweet['text']), self
            )
            v3.addWidget(self.label_retweet)
            
            if('thumbnail_pic' in retweet):
                self.pic_url = retweet['original_pic']
                self.label_thumbnail = PictureWidget()
                self.label_thumbnail.setMovie(self.thumbnail)
                v3.addWidget(self.label_thumbnail)
                
            h4 = QHBoxLayout()
            v3.addLayout(h4)
            str_time = time.strftime(self.time_format, time.localtime(retweet['created_at']))
            label_retweet_time = QLabel(str_time, self)
            self.btn_retweet_repost = TweetResponseButton('转发', retweet['reposts_count'], self)
            self.btn_retweet_comment = TweetResponseButton('评论', retweet['comments_count'], self)
            h4.addWidget(label_retweet_time)
            h4.addStretch()
            h4.addWidget(self.btn_retweet_repost)
            h4.addWidget(self.btn_retweet_comment)
        ## No retweet and has picture
        elif('thumbnail_pic' in self.tweet):
            self.pic_url = self.tweet['original_pic']
            self.label_thumbnail = PictureWidget()
            self.label_thumbnail.setMovie(self.thumbnail)
            #self.thumbnail.start()
            v2.addWidget(self.label_thumbnail)
            
        if self.label_thumbnail:
            size = self.label_thumbnail.movie().currentPixmap().size()
            self.label_thumbnail.setFixedSize(size)
        
        ## time, repost, comment
        h2 = QHBoxLayout()
        v2.addLayout(h2)
        str_time = time.strftime(self.time_format, time.localtime(self.tweet['created_at']))
        label_tweet_time = QLabel(str_time, self)
        self.btn_tweet_repost = TweetResponseButton('转发', self.tweet['reposts_count'], self)
        self.btn_tweet_comment = TweetResponseButton('评论', self.tweet['comments_count'], self)
        h2.addWidget(label_tweet_time)
        h2.addStretch()
        h2.addWidget(self.btn_tweet_repost)
        h2.addWidget(self.btn_tweet_comment)
        
        #v2.addStretch()
        self.response_widget = ResponseWidget(self.account.plugin, self.tweet, ResponseWidget.COMMENT, self)
        self.response_widget.hide()
        v2.addWidget(self.response_widget)
        self.connect(self.response_widget, SIGNAL_SUCCESSFUL_RESPONSE, self.onSuccessfulResponse)
        
    def renderUI(self):
        self.label_avatar.setCursor(QCursor(Qt.PointingHandCursor))
        if self.label_thumbnail:
            self.label_thumbnail.setCursor(QCursor(QPixmap(theme_manager.getParameter('Skin', 'zoom-in-cursor'))))
            
    def onSuccessfulResponse(self, widget_type):
        if widget_type == ResponseWidget.COMMENT:
            self.btn_tweet_comment.increaseAmount()
        elif widget_type == ResponseWidget.REPOST:
            self.btn_tweet_repost.increaseAmount()