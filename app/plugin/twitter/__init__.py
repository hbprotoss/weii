#coding=utf-8

import os
import urllib.parse
import json
import time
import hmac
import hashlib
import collections

from app.plugin import *
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DataStruct = collections.namedtuple('DataStruct', ['oauth_signature', 'oauth_nonce', 'oauth_timestamp'])

class Plugin(AbstractPlugin):
    '''
    Plugin for twitter
    '''
    
    def __init__(self, id, username, access_token, data, proxy):
        super(Plugin, self).__init__(id, username, access_token, data, proxy)
        
        self.service = 'twitter'
        self.service_icon = os.path.join(BASE_DIR, 'logo.jpg')
        self.time_format = '%a %b %d %H:%M:%S +0000 %Y'
        
        res = json.loads(data)
        self.consumer_key = res['consumer_key']
        self.consumer_secret = res['consumer_secret']
        self.access_token = res['access_token']
        self.access_token_secret = res['access_token_secret']
        self.app_params = {
            'oauth_consumer_key':self.consumer_key,
            'oauth_token':self.access_token,
            'oauth_version':'1.0',
            'oauth_signature_method':'HMAC-SHA1'
        }
        self.oauth_header = ''.join(
            ('OAuth oauth_consumer_key="%s"' % self.consumer_key,
             ', oauth_nonce="{oauth_nonce}"',
             ', oauth_signature="{oauth_signature}"',
             ', oauth_signature_method="HMAC-SHA1"',
             ', oauth_timestamp="{oauth_timestamp}"',
             ', oauth_token="%s"' % self.access_token,
             ', oauth_version="1.0"')
        )
        
    def calcSignature(self, method, url, params=None):
        '''
        @param method: string. Upper case name of method.
        @param url: string. Raw url string without UrlEncoding.
        @param params: dict. Both key and value are raw string without UrlEncoding.
        @return: string. Signature.
        '''
        d = dict(self.app_params)
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
        parameter_string = ''.join((encoded_list[0][0], '=', encoded_list[0][1]))
        for item in encoded_list[1:]:
            parameter_string += ''.join(('&', item[0], '=', item[1]))
            
        base_string = ''.join(
            (method.upper(), '&',
             urllib.parse.quote_plus(url.split('?', 1)[0]), '&',
             urllib.parse.quote_plus(parameter_string))
        )
        signing_key = ''.join(
            (urllib.parse.quote(self.consumer_secret),
             '&',
             urllib.parse.quote(self.access_token_secret))
        )
        hashed = hmac.new(signing_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
        binary_signature = hashed.digest()
        signature = base64.b64encode(binary_signature).decode('utf-8')
        
        return DataStruct._make((signature, d['oauth_nonce'], d['oauth_timestamp']))
    
    def getTimeline(self, id=None, max_point=None, count=20, page=1):
        rtn = None
        if id:
            pass
        else:
            url = 'https://api.twitter.com/1.1/statuses/home_timeline.json?%s'
            params = {
                'count': count,
                'page': page,
            }
            if max_point:
                params['max_id'] = max_point[0]
            params = urllib.parse.urlencode(params)
            
            data = self.calcSignature('GET', url % params)
            oauth_string = self.oauth_header.format(
                oauth_signature=urllib.parse.quote_plus(data.oauth_signature),
                oauth_nonce=data.oauth_nonce,
                oauth_timestamp=data.oauth_timestamp
            )
            rtn_from_server = self.getData(url % params, None,
                {'Authorization':oauth_string,
                 }
            )
            json_res = json.loads(rtn_from_server.decode())
            print(json_res)