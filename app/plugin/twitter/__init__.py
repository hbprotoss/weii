#coding=utf-8

import os
import urllib.parse
import json
import time
import hmac
import hashlib
import collections
import base64

from app.plugin import *
from app import config_manager

DataStruct = collections.namedtuple('DataStruct', ['oauth_signature', 'oauth_nonce', 'oauth_timestamp'])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSUMER_KEY = 'qKtlaEopAyp5wUdljmmlBg'
CONSUMER_SECRET = 'CILHlKVjMF6eoMwIrt3L3a2X00vXXunvM1gDaezYGc'
redirect_uri = 'https://api.weibo.com/oauth2/default.html'
authorize_url = 'https://api.twitter.com/oauth/authorize?oauth_token=%s'


class Plugin(AbstractPlugin):
    '''
    Plugin for twitter
    '''
    
    service = 'twitter'
    service_icon = os.path.join(BASE_DIR, 'logo.jpg')
        
    def __init__(self, id, username, access_token, data, proxy):
        super(Plugin, self).__init__(id, username, access_token, data, proxy)
        
        self.access_token = access_token
        self.access_token_secret = data
        self.app_params = {
            'oauth_consumer_key':CONSUMER_KEY,
            'oauth_token':self.access_token,
            'oauth_version':'1.0',
            'oauth_signature_method':'HMAC-SHA1'
        }
        self.oauth_header = ''.join(
            ('OAuth oauth_consumer_key="%s"' % CONSUMER_KEY,
             ', oauth_nonce="{oauth_nonce}"',
             ', oauth_signature="{oauth_signature}"',
             ', oauth_signature_method="HMAC-SHA1"',
             ', oauth_timestamp="{oauth_timestamp}"',
             ', oauth_token="%s"' % self.access_token,
             ', oauth_version="1.0"')
        )
        
        # First initialization
        if (id == '') and (username == ''):
            url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
            rtn_from_server = self.getData(url, None, self.getHeader('GET', url)).decode('utf-8')
            res = json.loads(rtn_from_server)
            
            self.id = res['id_str']
            self.username = res['name']
        
    def __transferAvatar(self, url):
        return ''.join(url.split('_normal'))
    
    def __transferTweet(self, tweet):
        tweet['reposts_count'] = tweet['retweet_count']
        tweet['comments_count'] = 0
        tweet['user']['avatar_large'] = self.__transferAvatar(tweet['user']['profile_image_url'])
        return tweet
        
    def getHeader(self, method, url, params=None):
        data = self.calcSignature(self.access_token, self.access_token_secret, method, url, params)
        oauth_string = self.oauth_header.format(
            oauth_signature = urllib.parse.quote_plus(data.oauth_signature),
            oauth_nonce = data.oauth_nonce,
            oauth_timestamp = data.oauth_timestamp
        )
        return {'Authorization':oauth_string}
    
    def getTimeline(self, id=None, max_point=None, count=20, page=1):
        rtn = None
        if id:
            pass
        else:
            params = {
                'count': count,
                'page': page,
            }
            if max_point and max_point[0] != 0:
                params['max_id'] = max_point[0]
                
            url = 'https://api.twitter.com/1.1/statuses/home_timeline.json?%s' % urllib.parse.urlencode(params)
            
            rtn_from_server = self.getData(url, None, self.getHeader('GET', url, params))
            json_res = json.loads(rtn_from_server.decode())
            
            for tweet in json_res:
                self.__transferTweet(tweet)
                if 'retweeted_status' in tweet:
                    self.__transferTweet(tweet['retweeted_status'])
            
            return json_res
            
    def getUserInfo(self, id='', screen_name=''):
        params = {}
        if id:
            params['user_id'] = id
        elif screen_name:
            params['screen_name'] = screen_name
        else:
            params['user_id'] = self.id
            
        url = 'https://api.twitter.com/1.1/users/show.json?%s' % urllib.parse.urlencode(params)
        rtn_from_server = self.getData(url, None, self.getHeader('GET', url, params))
        rtn = json.loads(rtn_from_server.decode())
        rtn['avatar_large'] = self.__transferAvatar(rtn['profile_image_url'])
        
        return rtn
        
    def getEmotions(self):
        return {}
    
    @staticmethod
    def getEmotionExpression():
        return ('', '')
    
    ####################################################
    # OAuth interface
    @staticmethod
    def calcSignature(access_token, access_token_secret, method, url, params=None):
        '''
        @param method: string. Upper case name of method.
        @param url: string. Raw url string without UrlEncoding.
        @param params: dict. Both key and value are raw string without UrlEncoding.
        @return: string. Signature.
        '''
        app_params = {
            'oauth_consumer_key':CONSUMER_KEY,
            'oauth_token':access_token,
            'oauth_version':'1.0',
            'oauth_signature_method':'HMAC-SHA1'
        }
        d = dict(app_params)
        if params:
            d.update(params)
        query = urllib.parse.urlsplit(url).query
        if query:
            d.update(urllib.parse.parse_qsl(query))
        time_and_nonce = str(int(time.time()))
        d['oauth_timestamp'] = time_and_nonce
        d['oauth_nonce'] = time_and_nonce
#        d['oauth_timestamp'] = '1318622958'
#        d['oauth_nonce'] = 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg'
        
        encoded_list = [(urllib.parse.quote(k), urllib.parse.quote(v))
                        for k,v in d.items()
                        ]
        encoded_list.sort(key=lambda x:x[0])
        parameter_string = '='.join(encoded_list[0])
        for item in encoded_list[1:]:
            parameter_string += ''.join(('&', item[0], '=', item[1]))
            
        base_string = ''.join(
            (method.upper(), '&',
             urllib.parse.quote_plus(url.split('?', 1)[0]), '&',
             urllib.parse.quote_plus(parameter_string))
        )
        signing_key = ''.join(
            (urllib.parse.quote(CONSUMER_SECRET),
             '&',
             urllib.parse.quote(access_token_secret))
        )
        hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
        binary_signature = hashed.digest()
        signature = base64.b64encode(binary_signature).decode('utf-8')
        
        return DataStruct._make((signature, d['oauth_nonce'], d['oauth_timestamp']))
    
    @staticmethod
    def getCallbackUrl():
        return redirect_uri
    
    @staticmethod
    def getAuthorize():
        time_and_nonce = str(int(time.time()))
        d = {
            'oauth_consumer_key': CONSUMER_KEY,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': time_and_nonce,
            'oauth_nonce': time_and_nonce,
            'oauth_version': '1.0',
            #'oauth_callback':redirect_uri
        }
        url = 'https://api.twitter.com/oauth/request_token'
        encoded_list = [(urllib.parse.quote(k), urllib.parse.quote(v))
                        for k,v in d.items()
                        ]
        encoded_list.sort(key=lambda x:x[0])
        params_string = '='.join(encoded_list[0])
        for item in encoded_list[1:]:
            params_string += ''.join(('&', item[0], '=', item[1]))
        base_string = ''.join(
            ('GET&',
             urllib.parse.quote_plus(url), '&',
             urllib.parse.quote_plus(params_string, safe='%'))
        )
        signing_key = ''.join(
            (urllib.parse.quote(CONSUMER_SECRET),
             '&')
        )
        signature = base64.b64encode(hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')
        
        # Request token
        #del d['oauth_callback']
        d['oauth_signature'] = signature
        req = urllib.request.Request(''.join((url, '?', urllib.parse.urlencode(d))))
        proxy = json.loads(config_manager.getParameter('Proxy'))
        for proxy_type,url in proxy.items():
            req.set_proxy(url, proxy_type)
        f = urllib.request.urlopen(req)
        response = f.read().decode('utf-8')
        log.debug(response)
        
        # Parse response from server
        parsed_res = {item[0]:item[1] for item in (seg.split('=') for seg in response.split('&'))}
        log.debug(parsed_res)
        return 'https://api.twitter.com/oauth/authenticate?oauth_token='+parsed_res['oauth_token'], parsed_res['oauth_token_secret']
    
    @staticmethod
    def getAccessToken(url, data):
        query = url.rsplit('?', 1)[-1]
        # oauth_token, oauth_verifier
        params = {item[0]:item[1] for item in (seg.split('=') for seg in query.split('&'))}
        params['oauth_token_secret'] = data
        # oauth_signature, oauth_nonce, oauth_timestamp
        signature, nonce, timestamp = Plugin.calcSignature(params['oauth_token'], params['oauth_token_secret'], 'GET', url)
        params['oauth_signature'] = signature
        params['oauth_nonce'] = nonce
        params['oauth_timestamp'] = timestamp
        
        params['oauth_signature_method'] = 'HMAC-SHA1'
        params['oauth_version'] = '1.0'
        
        url = 'https://api.twitter.com/oauth/access_token?%s' % urllib.parse.urlencode(params)
        log.debug(url)
        
        return (url, None, {})
    
    @staticmethod
    def parseData(data):
        res = {item[0]:item[1] for item in (seg.split('=') for seg in data.split('&'))}
        log.debug(res)
        return (res['oauth_token'], res['oauth_token_secret'])