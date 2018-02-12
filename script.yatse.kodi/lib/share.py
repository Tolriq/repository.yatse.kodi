# -*- coding: utf-8 -*-
import xbmc
import utils
import urllib

from utils import logger

def run(argument):
    if argument['type'] == 'magnet':
        openWith = utils.getSetting('openMagnetWith')
    	logger.info('Sharing magnet with %s' % openWith)
        if openWith == 'Elementum':
            utils.callPlugin('plugin://plugin.video.elementum/playuri?uri=' + urllib.quote_plus(argument['data']) + ')')
        elif openWith == 'Torrenter V2':
            utils.callPlugin('plugin://plugin.video.torrenter/?action=playSTRM&url=' + urllib.quote_plus(argument['data']) + ')')
        elif openWith == 'Quasar':
            utils.callPlugin('plugin://plugin.video.quasar/playuri?uri=' + urllib.quote_plus(argument['data']) + ')')
