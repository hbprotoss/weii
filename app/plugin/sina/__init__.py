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
        
        self.time_format = '%a %b %d %H:%M:%S +0800 %Y'
        self.new_time_format = '%Y-%m-%d %H:%M:%S'
        
    def getTimeline(self, id='', count=20, page=1, feature=0):
        rtn = None
        if(id):
            pass
        else:
            url = 'https://api.weibo.com/2/statuses/home_timeline.json?%s'
            params = urllib.parse.urlencode({
                'access_token': self.access_token,
                'count': count,
                'page': page
            })
            rtn_from_server = self.getData(url % params).decode('utf-8')
            rtn = json.loads(rtn_from_server)['statuses']
            
            for tweet in rtn:
                t = time.strptime(tweet['created_at'], self.time_format)
                tweet['created_at'] = time.strftime(self.new_time_format, t)
                if('retweeted_status' in tweet):
                    t = time.strptime(tweet['retweeted_status']['created_at'], self.time_format)
                    tweet['retweeted_status']['created_at'] = time.strftime(self.new_time_format, t)
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
    
    def getEmotionExpression(self):
        return ('[', ']')