#coding=utf-8

import os
import hashlib
import urllib.request
import imghdr

from PyQt4.QtGui import *

from app import constant
from app import logger

log = logger.getLogger(__name__)

class ResourceManager:
    '''
    Manager for bandwidth consuming resources.
    Get resources through memory, disk, Internet in turn.
    '''
    
    def __init__(self, username, resource_name, proxy={}):
        self.path = os.path.join(constant.DATA_ROOT, username, resource_name)
        try:
            os.makedirs(self.path)
        except:
            pass
        self.resource = {}
        self.opener = urllib.request.FancyURLopener(proxy)
        
    def setProxy(self, proxy):
        self.opener = urllib.request.FancyURLopener(proxy)
        
    def get(self, url):
        '''
        Get resource specified by url.
        @param url: string.
        '''
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # Resource in memory
        if url_hash in self.resource:
            log.info('Found in memory')
            return self.resource[url_hash]
        
        # Resource in disk
        abs_path = os.path.join(self.path, url_hash)
        if os.path.exists(abs_path):
            log.info('Found in disk')
            res = QPixmap(abs_path, imghdr.what(abs_path))
            self.resource[url_hash] = res
            return res
        
        # Resource from Internet
        log.info('Found from Internet')
        self.opener.retrieve(url, abs_path)
        res = QPixmap(abs_path, imghdr.what(abs_path))
        self.resource[url_hash] = res
        return res