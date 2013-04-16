# coding=utf-8

import sqlite3
import collections
import json

from app import constant

AccountDataStruct = collections.namedtuple('AccountDataStruct',
    ['id', 'username', 'access_token', 'data', 'proxy', 'service', 'send', 'receive']
)
connection = sqlite3.connect(constant.DATABASE)
c = connection.cursor()
c.execute('''
create table if not exists Accounts(
    id text,
    username text,
    access_token text,
    data text,
    proxy text, -- json format
    service text,
    send integer DEFAULT 1,  -- Whether chosen when post new tweet
    receive integer DEFAULT 1 -- Whether receive new tweets 
)
''')
connection.commit()
del c

########################################################################
# Exports
def getAccountsInfo():
    cursor = connection.cursor()
    cursor.execute('''select * from accounts''')
    return [AccountDataStruct._make(row) for row in cursor]

def createAccount(uid, username, access_token, data, proxy, service):
    cursor = connection.cursor()
    if isinstance(proxy, dict):
        proxy = json.dumps(proxy)
        
    t = (uid, username, access_token, data, proxy, service)
    cursor.execute('''insert into Accounts(id, username, access_token, data, proxy, service)
                                    values(?,?,?,?,?,?)''', t
    )
    connection.commit()
    
def deleteAccount(uid, service):
    cursor = connection.cursor()
    cursor.execute("delete from Accounts where id = ? and service = ?", (uid, service))
    connection.commit()
    
def setProxy(uid, service, proxy):
    cursor = connection.cursor()
    cursor.execute("update Accounts set proxy=? where id=? and service=?", (proxy, uid, service))
    connection.commit()