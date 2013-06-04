#coding=utf-8

import os
import hashlib
import urllib.request
import socket
from PyQt4.QtCore import *

from app import logger

socket.setdefaulttimeout(30)
log = logger.getLogger(__name__)

class ResourceManager:
    '''
    Manager for bandwidth consuming resources.
    Get resources through memory, disk, Internet in turn.
    '''
    # TODO: improve network module performance
    
    def __init__(self, path, proxy={}):
        self.path = path
        try:
            os.makedirs(self.path)
        except:
            pass
        self.resource = {}
        self.locks = {}             # URL hash to QMutex map
        self.query_lock = QMutex()  # Lock when query key in self.locks
        
        # Make a copy of proxy dict
        self.setProxy(dict(proxy))
        
    def setProxy(self, proxy={}):
        for k,v in proxy.items():
            if not v.startswith('http'):
                proxy[k] = ''.join(('http://', v))
        self.opener = urllib.request.URLopener(proxy)
        
    def get(self, url, report_hook=None):
        '''
        Get resource specified by url.
        @param url: string.
        @return: string. Absolute file path of resource.
        '''
        
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # Resource in memory
        if url_hash in self.resource:
            #log.debug('Found in memory')
            return self.resource[url_hash]
        
        self.query_lock.lock()
        if url_hash not in self.locks:
            self.locks[url_hash] = QReadWriteLock()
        self.query_lock.unlock()
        
        self.locks[url_hash].lockForRead()
        
        # Resource in disk
        abs_path = os.path.join(self.path, url_hash)
        if os.path.exists(abs_path):
            #log.debug('Found in disk')
            self.resource[url_hash] = abs_path
            
            if url_hash in self.locks:
                self.locks[url_hash].unlock()
                del self.locks[url_hash]
                
            return abs_path
        
        self.locks[url_hash].unlock()
        self.locks[url_hash].lockForWrite()
        # Resource from Internet
        #log.debug('Found from Internet')
        self.opener.retrieve(url, abs_path, report_hook)
        #res = QImage(abs_path, imghdr.what(abs_path))
        self.resource[url_hash] = abs_path
        
        self.locks[url_hash].unlock()
        del self.locks[url_hash]
        return abs_path