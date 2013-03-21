# coding=utf-8

import sqlite3
import collections
import json

from app import constant

AccountDataStruct = collections.namedtuple('AccountDataStruct',
    ['id', 'username', 'access_token', 'data', 'proxy', 'service']
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
    service text
)
''')
connection.commit()

########################################################################
# Exports
def getAccountsInfo():
    cursor = connection.cursor()
    cursor.execute('''select * from accounts''')
    return [AccountDataStruct._make(row) for row in cursor]

def writeSignleAccount(uid, username, access_token, data, proxy, service):
    cursor = connection.cursor()
    if isinstance(proxy, dict):
        proxy = json.dumps(proxy)
        
    t = (uid, username, access_token, data, proxy, service)
    cursor.execute("insert into Accounts values(?,?,?,?,?,?)", t)
    connection.commit()