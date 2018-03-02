# -*- coding: utf-8 -*-
import utils
import urlresolver
import urllib
import xbmc
import xbmcgui

from utils import logger

have_youtube_dl = "false"
try:
    from youtube_dl import YoutubeDL
    have_youtube_dl = "true"
except ImportError:
    logger.info("Youtube dl not present")

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
        url = urllib.unquote(argument['data'])
        logger.info('Trying to resolve with urlresolver: %s' % url)
        stream_url = urlresolver.HostedMediaFile(url = url).resolve()
        if not stream_url:
            if have_youtube_dl == "false":
                logger.error("Url not resolved and no YoutubeDL: %s" % url)
            else:
                logger.info('Trying to resolve with YoutubeDL: %s' % url)
                YoutubeDL_resolver = YoutubeDL({'format': 'best'})
                YoutubeDL_resolver.add_default_info_extractors()
                result = YoutubeDL_resolver.extract_info(url, download = False)
                if "url" in result:
                    stream_url = result["url"]
                    logger.info("Url resolved by YoutubeDL: %s" % result)
                else:
                    logger.error("Url not resolved: %s" % url)
        else:
            logger.info("Url resolved by urlResolver: %s" % stream_url)

        if stream_url:
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
        else:
            dialog = xbmcgui.Dialog()
            dialog.notification(utils.ADDON_NAME, utils.translation(32006), xbmcgui.NOTIFICATION_INFO, 5000)
