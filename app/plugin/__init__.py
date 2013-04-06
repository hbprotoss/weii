# coding=utf-8

import importlib
import os
import logging
import time
import urllib.request

from app import logger

##################################################################################
# Exceptions which can be raised
class weiBaseException(Exception):pass

class weiSizeError(weiBaseException):pass
class TweetTooLong(weiSizeError):pass
class TweetIsNull(weiSizeError):pass

class weiContentError(weiBaseException):pass
class RepeatContent(weiContentError):pass
class IllegalContent(weiContentError):pass

class weiStatusError(weiBaseException):pass
class TweetNotExists(weiStatusError):pass
class CommentNotExists(weiStatusError):pass
class PrivateNotExists(weiStatusError):pass
class DenyPrivate(weiStatusError):pass          # Private message is denied

class weiFollowerError(weiBaseException):pass
class AlreadyFollowed(weiFollowerError):pass
class FriendCountOutOfLimit(weiFollowerError):pass

class weiUnauthorizedError(weiBaseException):pass      # Access token error
class weiNetworkError(weiBaseException):pass
class weiUnknownError(weiBaseException):pass
class weiImageError(weiBaseException):pass


class AbstractPlugin():
    # TODO: Topic
    def __init__(self, uid, username, access_token, data, proxy={}):
        '''
        If both id and username are empty, it means the account is newly added and plugin should
        retrieve id and username from server with access_token.
        @param uid: string. User id.
        @param username: string.
        @param access_token: string.
        @param data: string. Custom data
        @param proxy: dict. {protocal:proxy_url}. e.g.{'http':'http://proxy.example.com:8080'}
        @return: None
        '''
        self.uid = uid
        self.username = username
        self.access_token = access_token
        self.data = data
        self.proxy = proxy
        self.new_time_format = '%Y-%m-%d %H:%M:%S'
        
    def setProxy(self, http, https):
        self.proxy = {'http': http, 'https': https}
        
    def getData(self, url, data=None, header={}):
        '''
        **********************************************************************
        * ATTENTION! This is the only way plugin interacts with the Internet.*
        * All traffic must go through this way in order to be controlled     *
        * under proxy settings.                                              *
        **********************************************************************
        Get data from specified url.
        If data is None, use GET method. Otherwise POST.
        @param url: string.
        @param data: string.
        @param header: dict. Header key and value pairs.
        @return: bytes.
        '''
        req = urllib.request.Request(url, data, header)
        for proxy_type, url in self.proxy.items():
            req.set_proxy(url, proxy_type)
        f = urllib.request.urlopen(req)
        return f.read()
    
    def _encodeMultipart(self, params_dict):
        '''
        Build a multipart/form-data body with generated random boundary.
        @param params_dict: dict. (key, value) pair of parameters. A file object means upload a file.
        '''
        #boundary = '----------%s' % hex(int(time.time() * 1000))
        boundary = '----------%s' % 'hbprotoss'
        data = []
        for k, v in params_dict.items():
            data.append('--%s' % boundary)
            if hasattr(v, 'read'):
                content = v.read()
                decoded_content = content.decode('ISO-8859-1')
                data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
                data.append('Content-Type: application/octet-stream\r\n')
                data.append(decoded_content)
            else:
                data.append('Content-Disposition: form-data; name="%s"\r\n' % k)
                data.append(v if isinstance(v, str) else v.decode('utf-8'))
        data.append('--%s--\r\n' % boundary)
        return '\r\n'.join(data).encode('ISO-8859-1'), boundary
    
    def getTweet(self, tid):
        '''
        Get single tweet
        @param tid: string. ID of tweet
        @return: Single tweet object. See documentation
        '''
        raise NotImplementedError
    
    def getTimeline(self, uid=None, max_point=None, count=20, page=1):
        '''
        Get user timeline
        @param uid: string. User ID. None means current user who has logged in.
        @param max_point: tuple(id, time). Returns results with an ID (or time) less than (that is, older than)
                          or equal to the specified ID (or time). None means return newest.
        @param count: int. Tweets per page
        @param page: int. Page number
        @return: List of tweet objects. See documentation
        '''
        raise NotImplementedError
    
    def getComment(self, cid, count=50, page=1):
        '''
        Get comments of tweet specified by id
        @param cid: string. Tweet ID
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of comment objects. See documentation
        '''
        raise NotImplementedError
    
    def getCommentToMe(self, count=50, page=1):
        '''
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of comment objects. See documentation
        '''
        raise NotImplementedError
    
    def getCommentByMy(self, count=50, page=1):
        '''
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of comment objects. See documentation
        '''
        raise NotImplementedError
    
    def getMentionedTweet(self, count=20, page=1):
        '''
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of tweet objects. See documentation
        '''
        raise NotImplementedError
    
    def getMentiondComment(self, count=20, page=1):
        '''
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of comment objects. See documentation
        '''
        raise NotImplementedError
    
    def getPrivate(self, count=20, page=1):
        '''
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of private message objects. See documentation
        '''
        raise NotImplementedError
    
    def getPrivateConversation(self, uid, count=20, page=1):
        '''
        Get private conversation with user specified by id
        @param uid: string. User ID
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of private message objects. See documentation
        '''
        raise NotImplementedError
    
    def getUserInfo(self, uid='', screen_name=''):
        '''
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param uid: string. User ID
        @param screen_name: string. User nick name
        @return: User object. See documentation
        '''
        raise NotImplementedError
    
    def getFriends(self, uid=0, screen_name='', count=50, page=1):
        '''
        Get friends list of user specified by id.
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param uid: string. User ID
        @param screen_name: string. User nick name
        @param count: int. Friends per page
        @param page: int. Page number
        @return: List of user objects. See documentation
        '''
        raise NotImplementedError
    
    def getFollowers(self, uid=0, screen_name='', count=50, page=1):
        '''
        Get followers list of user specified by id.
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param uid: string. User ID
        @param screen_name: string. User nick name
        @param count: int. Friends per page
        @param page: int. Page number
        @return: List of user objects. See documentation
        '''
        raise NotImplementedError
    
    def searchUser(self, q, count=10):
        '''
        @param q: string. Key words. (After URLEncoding)
        @param count: int. Number of users returned
        @return: List of search result objects. See documentation
        '''
        raise NotImplementedError
    
    def sendTweet(self, text, pic=None):
        '''
        @param text: string. Origin tweet text. URLs aren't shortened. No URLEncoding.
        @param pic: string. URI of picture to be attached. If None, then ignored.
        @return: Tweet object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendRetweet(self, tid, text, if_comment):
        '''
        @param tid: string. ID of tweet to be retweeted.
        @param text: string. Text of retweet. Origin text. URLs aren't shortened. No URLEncoding.
        @param if_comment: bool. If comment while retweeting. True to comment. False not to comment.
        @return: Tweet object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def deleteTweet(self, tid):
        '''
        @param tid: string. ID of tweet to be deleted.
        @return: Tweet object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendComment(self, tid, text, if_repost):
        '''
        @param tid: string. ID of tweet to be commented.
        @param text: string. Text of comment. Origin text. URLs aren't shortened. No URLEncoding.
        @param if_repost: bool. If repost while commenting. True to repost. False not to repost.
        @return: Comment object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendRecomment(self, tid, cid, text):
        '''
        Comment a comment
        @param tid: string. ID of tweet to be commented
        @param cid: string. ID of comment to be commented
        @param text: string. Text of comment. Origin text. URLs aren't shortened. No URLEncoding.
        @return: Comment object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def deleteComment(self, cid):
        '''
        @param cid: string. ID of comment to be deleted
        @return: Comment object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendPrivate(self, uid, text):
        '''
        Send private message
        @param uid: string. ID of user
        @param text: string. Text of comment. Origin text. URLs aren't shortened. No URLEncoding.
        @return: Private message object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def deletePrivate(self, tid):
        '''
        @param tid: string. ID of private message to be deleted.
        @return: Private message object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def follow(self, uid='', screen_name=''):
        '''
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param uid: string. User ID
        @param screen_name: string. User nick name
        @return: User object. See documentation
        '''
        raise NotImplementedError
    
    def unfollow(self, uid='', screen_name=''):
        '''
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param uid: string. User ID
        @param screen_name: string. User nick name
        @return: User object. See documentation
        '''
        raise NotImplementedError
    
    def isExpired(self):
        '''
        Return if the service(i.e. access_token) is expired.
        @return: True: Expired. False: Not Expired
        '''
        raise NotImplementedError
    
    def refresh(self):
        '''
        Refresh service status
        @return: None
        '''
        raise NotImplementedError
    
    def getEmotions(self):
        '''
        @return: Emotion object. See documentation
        '''
        raise NotImplementedError
    
    def getUnreads(self):
        '''
        @return: Unreaded message. See documentation
        '''
        raise NotImplementedError

    @staticmethod
    def getEmotionExpression():
        '''
        Get regex of emotion escape sequence
        @return: tuple. (prefix, suffix)
        '''
        raise NotImplementedError
    
    ########################################################
    # OAuth interface
    @staticmethod
    def getCallbackUrl():
        '''
        @return: Callback url of OAuth
        '''
        raise NotImplementedError
    
    @staticmethod
    def getAuthorize():
        '''
        @return: OAuth authorize url
        '''
        raise NotImplementedError
    
    @staticmethod
    def getAccessToken(url):
        '''
        @param url: Redirected by authorize url
        @return: (url, data, headers)
            url: url to get access token
            data: If None, use GET method. If not None, POST data
            headers: Additional HTTP headers. A dict of key and value
        '''
        raise NotImplementedError
    
    @staticmethod
    def parseData(data):
        '''
        @param data: Data returned by access token url
        @return: (access_token, data)
            access_token: string. Access token for OAuth 2.0. It can be empty string if using OAuth 1.x
            data: string. Custom data in any format to be stored in database. It is the plugin's
                responsibility to parse the data when plugin object is constructed.
        '''
        raise NotImplementedError
    
plugins = None
if __name__ == 'app.plugin':
    log = logger.getLogger(__name__)
    def loadPlugins():
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        log.info('Loading plugins')
        files = [file.split('.')[0]
                 for file in os.listdir(BASE_DIR)
                 if (not file.startswith('__'))]
        plugins = {file:importlib.import_module('plugin.' + file)
                   for file in files}
        log.info('Loading plugins done')
        for name,plugin in plugins.items():
            log.info('%s %s' % (name, str(plugin)))
        
        return plugins
    
    plugins = loadPlugins()
