# coding=utf-8

import importlib
import os
import logging

logging.basicConfig(level=logging.INFO)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.info('Loading plugins')
files = [file.split('.')[0]
         for file in os.listdir(BASE_DIR)
         if (not file.startswith('__'))]
plugins = {file:importlib.import_module('plugin.' + file)
           for file in files}
logging.info('Loading plugins done')
print(plugins)
for name,plugin in plugins.items():
    print(name, plugin.printMe())