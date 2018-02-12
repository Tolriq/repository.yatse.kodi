# -*- coding: utf-8 -*-
import xbmc
import utils

from utils import logger

def run(argument):
    if argument['type'] == 'magnet':
        openWith = utils.getSetting('openMagnetWith')
        logger.info('Sharing magnet with %s' % openWith)
        if openWith == 'Elementum':
            utils.callPlugin('plugin://plugin.video.elementum/playuri?uri=' + argument['data'] + ')')
        elif openWith == 'Torrenter V2':
            utils.callPlugin('plugin://plugin.video.torrenter/?action=playSTRM&url=' + argument['data'] + ')')
        elif openWith == 'Quasar':
            utils.callPlugin('plugin://plugin.video.quasar/playuri?uri=' + argument['data'] + ')')
