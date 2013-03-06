#coding=utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *

at_terminator = set(''' ~!@#$%^&*()+`={}|[]\;':",./<>?~！￥×（）、；：‘’“”《》？，。''')
url_legal = set('''!#$&'()*+,/:;=?@-._~'''
                + ''.join([chr(c) for c in range(ord('0'), ord('9')+1)])
                + ''.join([chr(c) for c in range(ord('a'), ord('z')+1)])
                + ''.join([chr(c) for c in range(ord('A'), ord('Z')+1)]))

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

class TweetWidget(QWidget):
    '''
    Widget for each tweet
    '''
    
    def __init__(self, account, tweet, avater, thumbnail, parent=None):
        '''
        @param account: misc.Account object
        @param tweet: dict of tweet. See doc/插件接口设计.pdf: 单条微博
        @param avater: QPixmap of user avater
        @param thumbnail: QMovie showing that the thumbnail is still loading from Internet
        @return: None
        '''
        super(TweetWidget, self).__init__(parent)
        
        self.account = account
        self.tweet = tweet
        self.avater = avater
        self.thumbnail = thumbnail
        
        self.setupUI()
        self.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        

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

        
    def renderUI(self, theme):
        '''
        @param theme: Theme.Theme object
        @return: None
        '''
        
    def setupUI(self):
        hLayout = QHBoxLayout()
        hLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(hLayout)
        
        # avater
        v1 = QVBoxLayout()
        hLayout.addLayout(v1)
        label_avater = QLabel(self)
        label_avater.setPixmap(self.avater)
        v1.addWidget(label_avater)
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
        label_service_icon.setPixmap(self.account.service_icon)
        h1.addWidget(label_user)
        #h1.addWidget(label_source)
        h1.addStretch()
        h1.addWidget(label_service_icon)
        
        ## tweet content
        label_tweet = TweetText(
            self.analyse(self.tweet['text']), self
        )
        v2.addWidget(label_tweet)
        
        ## retweet if exists
        if('retweeted_status' in self.tweet):
            retweet = self.tweet['retweeted_status']
            
            groupbox = QGroupBox(self)
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
            
            label_retweet = TweetText(
                self.analyse(retweet['text']), self
            )
            v3.addWidget(label_retweet)
            
            if(self.thumbnail):
                label_thumbnail = QLabel()
                label_thumbnail.setMovie(self.thumbnail)
                self.thumbnail.start()
                v3.addWidget(label_thumbnail)
                
            h4 = QHBoxLayout()
            v3.addLayout(h4)
            label_retweet_time = QLabel(retweet['created_at'], self)
            label_retweet_repost = QLabel('转发(%s)' % str(retweet['reposts_count']), self)
            label_retweet_comment = QLabel('评论(%s)' % str(retweet['comments_count']), self)
            h4.addWidget(label_retweet_time)
            h4.addStretch()
            h4.addWidget(label_retweet_repost)
            h4.addWidget(label_retweet_comment)
        ## No retweet and has picture
        elif(self.thumbnail):
            label_thumbnail = QLabel()
            label_thumbnail.setMovie(self.thumbnail)
            self.thumbnail.start()
            v2.addWidget(label_thumbnail)
        
        ## time, repost, comment
        h2 = QHBoxLayout()
        v2.addLayout(h2)
        label_tweet_time = QLabel(self.tweet['created_at'], self)
        label_tweet_repost = QLabel('转发(%s)' % str(self.tweet['reposts_count']), self)
        label_tweet_comment = QLabel('评论(%s)' % str(self.tweet['comments_count']), self)
        h2.addWidget(label_tweet_time)
        h2.addStretch()
        h2.addWidget(label_tweet_repost)
        h2.addWidget(label_tweet_comment)
        
        v2.addStretch()
#    def paintEvent(self, ev):
#        qp = QPainter()
#        qp.begin(self)
#        rect = self.geometry()
#        qp.drawLine(QPoint(rect.left(), rect.bottom()), QPoint(rect.right(), rect.bottom()))
#        qp.end()
#        return super(TweetWidget, self).paintEvent(ev)