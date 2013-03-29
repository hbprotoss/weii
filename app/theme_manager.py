#coding=utf-8

import os

from app import constant
from app import misc

INFO = 'Info'
SKIN = 'Skin'
ICON = 'Icon'
THEME_CONFIG = 'conf.ini'

class Theme():
    params = {}
    path = ''
    
    
# Internal
def __loadTheme( theme_name = 'default' ):
    '''
    @param theme_name: The name of theme
    @return: widget.theme.Theme object
    '''
    THEME_ROOT = os.path.join( constant.APP_ROOT, 'theme', theme_name )
    ICON_ROOT = os.path.join( THEME_ROOT, 'icon' )
    conf = misc.ConfParser()
    conf.read( os.path.join( THEME_ROOT, THEME_CONFIG ) )

    theme = Theme()
    theme.params[INFO] = dict( conf.items( INFO ) )
    theme.params[SKIN] = dict( conf.items( SKIN ) )
    theme.params[SKIN]['background-image'] = os.path.join( THEME_ROOT, theme.params[SKIN]['background-image'] )
    theme.params[SKIN]['loading-image'] = os.path.join( THEME_ROOT, theme.params[SKIN]['loading-image'] )
    theme.params[SKIN]['zoom-in-cursor'] = os.path.join(THEME_ROOT, theme.params[SKIN]['zoom-in-cursor'])
    theme.params[SKIN]['upload-pic'] = os.path.join(THEME_ROOT, theme.params[SKIN]['upload-pic'])
    theme.params[ICON] = {k:os.path.join( ICON_ROOT, v ) for k, v in conf.items( ICON )}
    theme.path = THEME_ROOT

    return theme

__g_theme = __loadTheme()


# Exports
def setCurrentTheme(theme_name):
    global __g_theme
    __g_theme = __loadTheme(theme_name)
    
def getCurrentTheme():
    return __g_theme
    
def getParameter(section, key):
    return __g_theme.params[section][key]

def getPath():
    return __g_theme.path
    