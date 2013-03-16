#coding=utf-8

import os
import urllib.parse
import json
import time
from app.plugin import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Plugin(AbstractPlugin):
    '''
    Plugin for sina
    '''
    
    def __init__(self, id, username, access_token, data, proxy):
        super(Plugin, self).__init__(id, username, access_token, data, proxy)
        
        self.service = 'sina'
        self.service_icon = os.path.join(BASE_DIR, 'logo.jpg')
        
        
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