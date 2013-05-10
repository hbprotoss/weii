# coding=utf-8

import sqlite3
import collections
import json
import atexit

from app import constant

AccountDataStruct = collections.namedtuple('AccountDataStruct',
    ['id', 'username', 'access_token', 'data', 'proxy', 'service', 'send', 'receive']
)
# FIXME: the parameter `check_same_thread` may be a potential bug here, cause the doc doesn't suggest it.
connection = sqlite3.connect(constant.DATABASE, check_same_thread=False)
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
c.execute('''
create table if not exists Timeline(
    id integer PRIMARY KEY AUTOINCREMENT,
    content text,    -- json format
    service text,
    uid text
)
''')
c.execute('''
create table if not exists Mention(
    id integer PRIMARY KEY AUTOINCREMENT,
    content text,    -- json format
    service text,
    uid text
)
''')
c.execute('''
create table if not exists Comment(
    id integer PRIMARY KEY AUTOINCREMENT,
    content text,    -- json format
    service text,
    uid text
)
''')
connection.commit()
del c

def onExit():
    tables = ['Timeline', 'Comment', 'Mention']
    cursor = connection.cursor()
    for table in tables:
        cursor.execute('''
        delete from %s 
        where id not in 
            (select id from %s order by id desc limit 40)
        ''' % (table, table))
    connection.commit()

atexit.register(onExit)
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
    
def getHistory(table):
    '''
    @param table: string. Table name
    '''
    cursor = connection.cursor()
    cursor.execute('''select content,service,uid from %s''' % table)
    return list(cursor)

def insertHistory(table, contents, service, uid):
    '''
    @param table: string. Table name.
    @param contents: list of strings. Content to be inserted.
    '''
    cursor = connection.cursor()
    for content in contents:
        cursor.execute("insert into %s(content,service,uid) values(?, ?, ?)" % table, (content, service, uid))
    connection.commit()