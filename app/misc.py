#coding=utf-8

import configparser

# Global variable
main_window = None

class ConfParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr