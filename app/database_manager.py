# coding=utf-8

import sqlite3
import collections
from app import constant

AccountDataStruct = collections.namedtuple('AccountDataStruct',
    ['id', 'username', 'access_token', 'data', 'proxy', 'service']
)
connection = sqlite3.connect(constant.DATABASE)

# Exports
def getAccountsInfo():
    cursor = connection.cursor()
    cursor.execute('''select * from accounts''')
    return [AccountDataStruct._make(row) for row in cursor]