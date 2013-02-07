#coding=utf-8

import configparser

class ConfParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr