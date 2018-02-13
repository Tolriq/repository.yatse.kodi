# -*- coding: utf-8 -*-
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
        import xbmc
        import xbmcgui
        url = urllib.unquote(argument['data'])
        logger.info('Trying to resolve with urlresolver: %s' % url)
        stream_url = urlresolver.HostedMediaFile(url = url).resolve()
        if not stream_url:
            dialog = xbmcgui.Dialog()
            dialog.notification(utils.ADDON_NAME, utils.translation(32006), xbmcgui.NOTIFICATION_INFO, 5000)
            logger.error("Url not resolved: %s" % url)
        else:
            if (not 'queue' in argument) or (argument['queue'] == "false") or (not xbmc.Player().isPlaying()):
                logger.info('Playing resolved url: %s' % stream_url)
                xbmc.Player().play(stream_url)
            else:
                if xbmc.Player().isPlayingAudio():
                    logger.info('Queuing to music resolved url: %s' % stream_url)
                    xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(stream_url)
                else:
                    logger.info('Queuing to video resolved url: %s' % stream_url)
                    xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(stream_url)