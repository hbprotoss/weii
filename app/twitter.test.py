#!/usr/bin/env python3

import json
from app.plugin import twitter

d = {
    'consumer_key':'qKtlaEopAyp5wUdljmmlBg',
    'consumer_secret':'CILHlKVjMF6eoMwIrt3L3a2X00vXXunvM1gDaezYGc',
    'access_token':'166817375-J0oDWXIHdvjxNIJndR3hFNTMgo9gXloCnFSFc4em',
    'access_token_secret':'WTNaYDJLfOSAVef1vzqdgUQ54gPewyth5gVxFdHY1E'
}
#d = {
#    'consumer_key':'xvz1evFS4wEEPTGEFPHBog',
#    'consumer_secret':'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw',
#    'access_token':'370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb',
#    'access_token_secret':'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE'
#}

t = twitter.Plugin(0, 'hbprotoss', '', json.dumps(d),
    {'https':'http://127.0.0.1:10001', 'http':'http://127.0.0.1:10001'}
)
params = {
    'status':'Hello Ladies + Gentlemen, a signed OAuth request!',
    'include_entities':'true'
}
#print(t.calcSignature('GET', 'https://api.twitter.com/1.1/statuses/home_timeline.json', None))
t.getTimeline()