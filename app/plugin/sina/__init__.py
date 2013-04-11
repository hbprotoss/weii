#coding=utf-8

import os
import urllib.parse
import json
import time
from app.plugin import *
from app import config_manager
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

##################################################################################################
# OAuth data
KEY = '2933789200'
SECRET = 'ea6beb430e6fadc8345bde9a8b6bd137'
redirect_uri = 'https://api.weibo.com/oauth2/default.html'
authorize_url = 'https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s' % (KEY, redirect_uri)
access_token_url = 'https://api.weibo.com/oauth2/access_token'

# Map of error code to plugin exception
exception_dict = {
    '10013': weiUnauthorizedError,
    '20005': weiImageError,
    '20006': weiImageError,
    '20007': weiImageError,
    '20008': TweetIsNull,
    '20012': TweetTooLong,
    '20013': TweetTooLong,
    '20017': RepeatContent,
    '20111': RepeatContent,
    '20019': RepeatContent,
    '20018': IllegalContent,
    '20020': IllegalContent,
    '20021': IllegalContent,
    '20101': TweetNotExists,
    '20201': CommentNotExists,
    '20504': weiFollowerError,
    '20513': FriendCountOutOfLimit,
    '20506': AlreadyFollowed,
    '21314': weiUnauthorizedError,
    '21315': weiUnauthorizedError,
    '21316': weiUnauthorizedError,
    '21317': weiUnauthorizedError,
    '21327': weiUnauthorizedError,
}

def sinaMethod(func):
    '''
    Decorator to handle error code returned by sina
    '''
    def func_wrapper(*args, **kwargs):
        try:
            raw_rtn = func(*args, **kwargs)
        except urllib.error.HTTPError as e:
            if e.fp:
                # Sina app error
                error_msg = json.loads(e.fp.read().decode('utf-8'))
                error_code = str(error_msg['error_code'])
                if error_code in exception_dict:
                    raise exception_dict[error_code](error_msg['error'])
                else:
                    log.error('Unknown error %s' % e)
                    raise weiUnknownError(str(e))
            else:
                # Network error
                raise weiNetworkError(str(e))
        else:
            return raw_rtn
    return func_wrapper

class Plugin(AbstractPlugin):
    '''
    Plugin for sina
    '''
    
    service = 'sina'
    service_icon = os.path.join(BASE_DIR, 'logo.jpg')
    
    def __init__(self, uid, username, access_token, data='', proxy={}):
        super(Plugin, self).__init__(uid, username, access_token, data, proxy)
        
        if (uid == '') and (username == ''):
            url = 'https://api.weibo.com/2/account/get_uid.json?access_token=%s' % access_token
            self.proxy = json.loads(config_manager.getParameter('Proxy'))
            
            rtn_from_server = self.getData(url).decode('utf-8')
            self.uid = json.loads(rtn_from_server)['uid']
            
            user_info = self.getUserInfo(self.uid)
            self.username = user_info['screen_name']
        
    @sinaMethod
    def getTimeline(self, uid=None, max_point=None, count=20, page=1):
        rtn = None
        if(uid):
            # TODO: get timeline of user specified by uid.
            pass
        else:
            url = 'https://api.weibo.com/2/statuses/home_timeline.json?%s'
            params = urllib.parse.urlencode({
                'access_token': self.access_token,
                'count': count,
                'page': page,
                'max_id': str(max_point[0]) if max_point else '0'
            })
            rtn_from_server = self.getData(url % params).decode('utf-8')
            rtn = json.loads(rtn_from_server)['statuses']
            
            for tweet in rtn:
                if('deleted' in tweet):
                    tweet['created_at'] = ''
                    tweet['reposts_count'] = 0
                    tweet['comments_count'] = 0
                    tweet['user'] = {'screen_name':'微博小秘书'}
                
                if('retweeted_status' in tweet):
                    retweet = tweet['retweeted_status']
                    if('deleted' in retweet):
                        retweet['created_at'] = ''
                        retweet['reposts_count'] = 0
                        retweet['comments_count'] = 0
                        retweet['user'] = {'screen_name':'微博小秘书'}
        return rtn
    
    @sinaMethod
    def getUserInfo(self, uid='', screen_name=''):
        params = dict([('access_token', self.access_token)])
        if uid:
            params['uid'] = uid
        elif screen_name:
            params['screen_name'] = screen_name
        else:
            params['uid'] = self.uid
            
        url = 'https://api.weibo.com/2/users/show.json?%s'
        rtn_from_server = self.getData(url % urllib.parse.urlencode(params)).decode('utf-8')
        rtn = json.loads(rtn_from_server)
        
        return rtn
    
    @sinaMethod
    def getMentions(self, max_point=None, count=20, page=1):
        url = 'https://api.weibo.com/2/statuses/mentions.json?%s'
        params = {
            'access_token': self.access_token,
            'count': count,
            'page': page,
            'max_id': str(max_point[0]) if max_point else '0'
        }
        rtn_from_server = self.getData(url % urllib.parse.urlencode(params)).decode('utf-8')
        rtn = json.loads(rtn_from_server)['statuses']
        
        return rtn
    
    @sinaMethod
    def getComment(self, max_point=None, count=20, page=1):
        url = 'https://api.weibo.com/2/comments/timeline.json?%s'
        params = {
            'access_token': self.access_token,
            'count': count,
            'page': page,
            'max_id': str(max_point[0]) if max_point else '0'
        }
        rtn_from_server = self.getData(url % urllib.parse.urlencode(params)).decode('utf-8')
        rtn = json.loads(rtn_from_server)['comments']
        
        return rtn
    
    @sinaMethod
    def getEmotions(self):
        params = dict([('access_token', self.access_token)])
        url = 'https://api.weibo.com/2/emotions.json?%s'
        rtn_from_server = self.getData(url % urllib.parse.urlencode(params)).decode('utf-8')
        json_res = json.loads(rtn_from_server)
        
        rtn = {}
        for emotion in json_res:
            category = emotion['category']
            if category == '':
                category = '默认'
                
            if category not in rtn:
                rtn[category] = []
            rtn[category].append({'name':emotion['value'], 'url':emotion['url']})
            pass
        #print(rtn.keys())
        
        return rtn
    
    @sinaMethod
    def sendTweet(self, text, pic=None):
        params = {
            'access_token': self.access_token,
            'status': urllib.parse.quote(text)
        }
        if pic:
            url = 'https://upload.api.weibo.com/2/statuses/upload.json'
            params['pic'] = open(pic, 'rb')
            encoded_params, boundary = self._encodeMultipart(params)
            headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary}
        else:
            url = 'https://api.weibo.com/2/statuses/update.json'
            encoded_params = urllib.parse.urlencode(params, safe='%').encode('utf-8')
            headers = {}
            
        #log.debug(encoded_params)
        rtn_from_server = self.getData(url, encoded_params, headers)
        rtn = json.loads(rtn_from_server.decode('utf-8'))
        return rtn
    
    @sinaMethod
    def sendComment(self, tid, text, if_repost=False):
        # TODO: if_repost
        url = 'https://api.weibo.com/2/comments/create.json'
        params = urllib.parse.urlencode({
            'access_token': self.access_token,
            'id': tid,
            'comment': text
        }).encode('utf-8')
        rtn_from_server = self.getData(url, params).decode('utf-8')
        rtn = json.loads(rtn_from_server)
        return rtn
    
    @sinaMethod
    def sendRecomment(self, tid, cid, text):
        url = 'https://api.weibo.com/2/comments/reply.json'
        params = urllib.parse.urlencode({
            'access_token': self.access_token,
            'id': tid,
            'cid': cid,
            'comment': text
        }).encode('utf-8')
        rtn_from_server = self.getData(url, params).decode('utf-8')
        rtn = json.loads(rtn_from_server)
        return rtn
    
    @sinaMethod
    def sendRetweet(self, tid, text, if_comment=False):
        # TODO: if_comment
        # temporary code
        if len(text)> 140:
            text = text[:140]
            
        url = 'https://api.weibo.com/2/statuses/repost.json'
        params = urllib.parse.urlencode({
            'access_token': self.access_token,
            'id': tid,
            'status': text,
            'is_comment': int(if_comment)
        }).encode('utf-8')
        rtn_from_server = self.getData(url, params).decode('utf-8')
        rtn = json.loads(rtn_from_server)
        return rtn
    
    @sinaMethod
    def getUnreads(self):
        url = 'https://rm.api.weibo.com/2/remind/unread_count.json?access_token=%s' % self.access_token
        rtn_from_server = self.getData(url).decode('utf-8')
        unreads = json.loads(rtn_from_server)
        rtn = {
            'tweet': unreads['status'],
            'follower': unreads['follower'],
            'comment': unreads['cmt'],
            'mention': unreads['mention_cmt'] + unreads['mention_status'],
            'private': unreads['dm']
        }
        return rtn
    
    @staticmethod
    def getEmotionExpression():
        return ('[', ']')
    
    #############################################################
    # OAuth interface
    @staticmethod
    def getCallbackUrl():
        return redirect_uri
    
    @staticmethod
    def getAuthorize():
        return authorize_url
    
    @staticmethod
    def getAccessToken(url):
        code = url.rsplit('=', 1)[-1]
        data_dict = {
            'client_id': KEY,
            'client_secret': SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code
        }
        return (access_token_url, urllib.parse.urlencode(data_dict), {})
    
    @staticmethod
    def parseData(data):
        res = json.loads(data)
        return (res['access_token'], '')
    
