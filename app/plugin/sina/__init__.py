#coding=utf-8

import os
import urllib.parse
import json
import time
from app.plugin import *
from app import config_manager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

##################################################################################################
# OAuth data
KEY = '2933789200'
SECRET = 'ea6beb430e6fadc8345bde9a8b6bd137'
redirect_uri = 'https://api.weibo.com/oauth2/default.html'
authorize_url = 'https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s' % (KEY, redirect_uri)
access_token_url = 'https://api.weibo.com/oauth2/access_token'

class Plugin(AbstractPlugin):
    '''
    Plugin for sina
    '''
    
    service = 'sina'
    service_icon = os.path.join(BASE_DIR, 'logo.jpg')
    
    def __init__(self, id, username, access_token, data='', proxy={}):
        super(Plugin, self).__init__(id, username, access_token, data, proxy)
        
        if (id == '') and (username == ''):
            url = 'https://api.weibo.com/2/account/get_uid.json?access_token=%s' % access_token
            self.proxy = json.loads(config_manager.getParameter('Proxy'))
            
            rtn_from_server = self.getData(url).decode('utf-8')
            self.id = json.loads(rtn_from_server)['uid']
            
            user_info = self.getUserInfo(self.id)
            self.username = user_info['screen_name']
        
    def getTimeline(self, id=None, max_point=None, count=20, page=1):
        rtn = None
        if(id):
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
    
    def getUserInfo(self, id='', screen_name=''):
        params = dict([('access_token', self.access_token)])
        if id:
            params['uid'] = id
        elif screen_name:
            params['screen_name'] = screen_name
        else:
            params['uid'] = self.id
            
        url = 'https://api.weibo.com/2/users/show.json?%s'
        rtn_from_server = self.getData(url % urllib.parse.urlencode(params)).decode('utf-8')
        rtn = json.loads(rtn_from_server)
        
        return rtn
    
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
    
    @staticmethod
    def getUidAndUsername(access_token, access_token_secret):
        url = 'https://api.weibo.com/2/account/get_uid.json?%s' % access_token
        opener = urllib.request.FancyURLopener(json.loads(config_manager.getParameter('Proxy')))
        f = opener.open(url)
        uid = json.loads(f.read().decode('utf-8'))['uid']