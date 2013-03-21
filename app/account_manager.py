# coding=utf-8

import os
from collections import namedtuple
import json
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from app import plugin
from app import resource_manager
from app import constant
from app import database_manager

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
    
    def setProxy(self, host, port):
        # TODO: setProxy
        proxy = ''.join(('http://', host, ':', port))
        self.plugin.setProxy(proxy, proxy)
        pass
    
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
    #return dummyInitAccount()
    plugins = plugin.plugins
    rtn = []
    for account in database_manager.getAccountsInfo():
        acc = Account(
            plugins[account.service].Plugin(
                account.id, account.username, account.access_token, account.data, json.loads(account.proxy)
            )
        )
        rtn.append(acc)
    return rtn

account_list = initAccount()
# Mapping of username to Account object.
# Special: all_accounts maps to the whole list.
all_accounts = {account.plugin.username:[account] for account in account_list}
all_accounts[ALL_ACCOUNTS] = account_list
current_list = all_accounts[ALL_ACCOUNTS]

# Object to emit signal such as SIGNAL_ACCOUNT_ADDED
signal_emitter = QObject()
# Signals
SIGNAL_ACCOUNT_ADDED = SIGNAL('AccountAdded')
SIGNAL_ACCOUNT_DELETED = SIGNAL('AccountDeleted')

###############################################################################
# Exports
def getEmitter():
    return signal_emitter

def getCurrentAccount():
    '''
    @return: List of current account. If only one account is chosen, the list contains only the current Account
             object. If all accounts are chosen, the list contains all Account objects. 
    '''
    return list(current_list)

def setCurrentAccount(username):
    current_list = all_accounts[username]
    
def getAllAccount():
    return account_list

def addAccount(service, uid, username, access_token, data='', proxy={}):
    plugin_obj = plugin.plugins[service].Plugin(uid, username, access_token, data, proxy)
    account = Account(plugin_obj)
    account_list.append(account)
    all_accounts[plugin_obj.username] = [account]
    
    database_manager.createAccount(plugin_obj.id, plugin_obj.username, access_token, data, proxy, service)
    
    # Emit signal
    signal_emitter.emit(SIGNAL_ACCOUNT_ADDED, account)
    return account

def deleteAccount(account):
    del all_accounts[account.plugin.username]
    account_list.remove(account)
    database_manager.deleteAccount(account.plugin.id, account.plugin.service)
    
    # Emit signal
    signal_emitter.emit(SIGNAL_ACCOUNT_DELETED, account)
    
    del account