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
    elif argument['type'] == 'unresolvedurl':
        import urlresolver
        import urllib
        import xbmcgui
        url = urllib.unquote(argument['data'])
        logger.info('Trying to resolve with urlresolver: %s' % url)
        stream_url = urlresolver.HostedMediaFile(url = url).resolve()
        if not stream_url:
            dialog = xbmcgui.Dialog()
            dialog.notification(utils.ADDON_NAME, utils.translation(32006), xbmcgui.NOTIFICATION_INFO, 5000)
            logger.error("Url not resolved: %s" % url)
        else:
            logger.info('Url resolved to: %s' % stream_url)
            xbmc.Player().play(stream_url)
            