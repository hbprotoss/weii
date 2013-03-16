# coding=utf-8

import os
from collections import namedtuple
import json
from PyQt4.QtGui import *

from app import plugin
from app import resource_manager
from app import constant

EmotionExp = namedtuple('EmotionExp', ['prefix', 'suffix'])
ALL_ACCOUNTS = 'all_accounts'

class Account:
    def __init__(self, account_plugin):
        # Plugin object
        self.plugin = account_plugin
        
        # QImage object
        self.service_icon = QImage(self.plugin.service_icon)
        
        # Resource manager
        self.emotion_manager = resource_manager.ResourceManager(
            os.path.join(plugin.plugins[account_plugin.service].BASE_DIR, 'emotion'), account_plugin.proxy)
        self.avatar_manager = resource_manager.ResourceManager(
            os.path.join(constant.DATA_ROOT, account_plugin.username, 'avatar'), account_plugin.proxy)
        self.picture_manager = resource_manager.ResourceManager(
            os.path.join(constant.DATA_ROOT, account_plugin.username, 'picture'), account_plugin.proxy)
        
        # emotion_list contains category information. Used when posting tweet
        try:
            self.emotion_list = json.load(open(self.emotion_manager.path+'/emotion.json'))
        except IOError:
            self.emotion_list = self.plugin.getEmotions()
            json.dump(self.emotion_list, open(self.emotion_manager.path+'/emotion.json', 'w'))
            
        # emotion_dict contains name to url mapping
        self.emotion_dict = self.getEmotionDict(self.emotion_list)
            
        self.emotion_exp = EmotionExp._make(self.plugin.getEmotionExpression())
        
        # for append new tweet
        self.last_tweet_id = None
        self.last_tweet_time = None
        
    def getEmotionDict(self, emotion_list):
        rtn = {}
        for category in emotion_list.keys():
            for emotion in emotion_list[category]:
                rtn[emotion['name']] = emotion['url']
                
        return rtn
    
# Internal
def dummyInitAccount():
    '''
    Initiate all accounts stored in database
    @return: List of Account objects
    '''
    # debug
    plugins = plugin.plugins
    sina = Account(
        plugins['sina'].Plugin(
            '1778908794', '_hbprotoss', '2.0018H5wBeasXMD00288e252cov2YBC', None, {})
            #{'http':'http://127.0.0.1:10001', 'https':'http://127.0.0.1:10001'}),
    )
    data = {
        'access_token':'166817375-J0oDWXIHdvjxNIJndR3hFNTMgo9gXloCnFSFc4em',
        'access_token_secret':'WTNaYDJLfOSAVef1vzqdgUQ54gPewyth5gVxFdHY1E'
    }
    twitter = Account(
        plugins['twitter'].Plugin(
            '166817375', 'hbprotoss', '', json.dumps(data),
            {'http':'http://127.0.0.1:10001', 'https':'http://127.0.0.1:10001'}
        )
    )
    
    #return [sina]
    return [sina, twitter]

def initAccount():
    '''
    Initiate all accounts stored in database
    @return: List of Account objects
    '''
    # TODO: Initiate from database
    return dummyInitAccount()

account_list = initAccount()
# Mapping of username to Account object.
# Special: all_accounts maps to the whole list.
all_accounts = {account.plugin.username:[account] for account in account_list}
all_accounts[ALL_ACCOUNTS] = account_list
# TODO: Default to all accounts
#current_list = all_accounts['_hbprotoss']
current_list = all_accounts[ALL_ACCOUNTS]

# Exports
def getCurrentAccount():
    '''
    @return: List of current account. If only one account is chosen, the list contains only the current Account
             object. If all accounts are chosen, the list contains all Account objects. 
    '''
    return current_list

def setCurrentAccount(username):
    current_list = all_accounts[username]

def addAccount(account):
    all_accounts[account.username] = [account]
    account_list.append(account)

def removeAccount(account):
    del all_accounts[account.plugin.username]