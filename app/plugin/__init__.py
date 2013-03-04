# coding=utf-8

import importlib
import os
import logging
import urllib.request

from app import logger

##################################################################################
# Exceptions which can be raised
class weiSizeError(Exception):pass
class TweetTooLong(weiSizeError):pass
class TweetIsNull(weiSizeError):pass
class ImageTooLarge(weiSizeError):pass

class weiContentError(Exception):pass
class OutOfRateLimit(weiContentError):pass      # Publish tweet too frequently
class RepeatContent(weiContentError):pass
class IllegalContent(weiContentError):pass
class Advertising(weiContentError):pass

class weiStatusError(Exception):pass
class TweetNotExists(weiStatusError):pass
class CommentNotExists(weiStatusError):pass
class PrivateNotExists(weiStatusError):pass
class DenyPrivate(weiStatusError):pass          # Private message is denied

class weiFollowerError(Exception):pass
class CannotFollowSelf(weiFollowerError):pass
class AlreadyFollowed(weiFollowerError):pass
class FriendCountOutOfLimit(weiFollowerError):pass

class weiNetworkError(Exception):pass


class AbstractPlugin():
    def __init__(self, id, username, access_token, data, proxy={}):
        '''
        @param id: string. User id.
        @param username: string.
        @param access_token: string.
        @param data: string. Custom data
        @param proxy: dict. {protocal:proxy_url}. e.g.{'http':'http://proxy.example.com:8080'}
        @return: None
        '''
        self.id = id
        self.username = username
        self.access_token = access_token
        self.data = data
        self.opener = urllib.request.FancyURLopener(proxy)
        
    def getData(self, url, data=None):
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
        @return: bytes.
        '''
        f = self.opener.open(url, data)
        return f.read()
    
    def getTweet(self, id):
        '''
        Get single tweet
        @param id: string. ID of tweet
        @return: Single tweet object. See documentation
        '''
        raise NotImplementedError
    
    def getTimeline(self, id='', count=20, page=1, feature=0):
        '''
        Get user timeline
        @param id: string. User ID. '' Means current user who has logged in.
        @param count: int. Tweets per page
        @param page: int. Page number
        @param feature: int. Tweets type. See documentation. (This parameter can be ignored)
        @return: List of tweet objects. See documentation
        '''
        raise NotImplementedError
    
    def getComment(self, id, count=50, page=1):
        '''
        Get comments of tweet specified by id
        @param id: string. Tweet ID
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
    
    def getPrivateConversation(self, id, count=20, page=1):
        '''
        Get private conversation with user specified by id
        @param id: string. User ID
        @param count: int. Comments per page
        @param page: int. Page number
        @return: List of private message objects. See documentation
        '''
        raise NotImplementedError
    
    def getUserInfo(self, id='', screen_name=''):
        '''
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param id: string. User ID
        @param screen_name: string. User nick name
        @return: User object. See documentation
        '''
        raise NotImplementedError
    
    def getFriends(self, id=0, screen_name='', count=50, page=1):
        '''
        Get friends list of user specified by id.
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param id: string. User ID
        @param screen_name: string. User nick name
        @param count: int. Friends per page
        @param page: int. Page number
        @return: List of user objects. See documentation
        '''
        raise NotImplementedError
    
    def getFollowers(self, id=0, screen_name='', count=50, page=1):
        '''
        Get followers list of user specified by id.
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param id: string. User ID
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
    
    def getEmotions(self):
        '''
        @return: Emotion object. See documentation
        '''
        raise NotImplementedError
    
    def sendTweet(self, text, pic=None):
        '''
        @param text: string. Origin tweet text. URLs aren't shortened. No URLEncoding.
        @param pic: string. URI of picture to be attached. If None, then ignored.
        @return: Tweet object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendRetweet(self, id, text):
        '''
        @param id: string. ID of tweet to be retweeted.
        @param text: string. Text of retweet. Origin text. URLs aren't shortened. No URLEncoding.
        @return: Tweet object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def deleteTweet(self, id):
        '''
        @param id: string. ID of tweet to be deleted.
        @return: Tweet object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendComment(self, id, text):
        '''
        @param id: string. ID of tweet to be commented.
        @param text: string. Text of comment. Origin text. URLs aren't shortened. No URLEncoding.
        @return: Comment object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendRecomment(self, id, cid, text):
        '''
        Comment a comment
        @param id: string. ID of tweet to be commented
        @param cid: string. ID of comment to be commented
        @param text: string. Text of comment. Origin text. URLs aren't shortened. No URLEncoding.
        @return: Comment object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def deleteComment(self, id):
        '''
        @param id: string. ID of comment to be deleted
        @return: Comment object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def sendPrivate(self, id, text):
        '''
        Send private message
        @param id: string. ID of user
        @param text: string. Text of comment. Origin text. URLs aren't shortened. No URLEncoding.
        @return: Private message object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def deletePrivate(self, id):
        '''
        @param id: string. ID of private message to be deleted.
        @return: Private message object returned by server. See documentation
        '''
        raise NotImplementedError
    
    def follow(self, id='', screen_name=''):
        '''
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param id: string. User ID
        @param screen_name: string. User nick name
        @return: User object. See documentation
        '''
        raise NotImplementedError
    
    def unfollow(self, id='', screen_name=''):
        '''
        You must supply one and only one parameter between id and screen_name.
        If both supplied, we choose id.
        @param id: string. User ID
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
    
    def getEmotionExpression(self):
        '''
        Get regex of emotion escape sequence
        @return: tuple. (prefix, suffix)
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
            print(name, plugin)
        
        return plugins
    
    plugins = loadPlugins()
