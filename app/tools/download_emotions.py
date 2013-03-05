#!/usr/bin/env python3

import sys
import os
import json
import urllib.request
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')))
import app.plugin

try:
    os.mkdir('emotion')
except:
    pass

plugin_name = sys.argv[1]
plugin = app.plugin.plugins[plugin_name]
instance = plugin.Plugin(sys.argv[2], sys.argv[3], sys.argv[4], None, {})

emotion_list = instance.getEmotions()
json.dump(emotion_list, open('emotion/emotion.json', 'w'))

for category in emotion_list.keys():
    print(category)
    for emotion in emotion_list[category]:
        url = emotion['url']
        url_hash = hashlib.md5(url.encode('utf8')).hexdigest()
        urllib.request.urlretrieve(url, 'emotions/' + url_hash)
        print('%s -> %s done' % (emotion['name'], url_hash))