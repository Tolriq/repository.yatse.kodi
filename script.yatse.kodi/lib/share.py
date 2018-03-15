# -*- coding: utf-8 -*-
import urllib

import urlresolver

import utils
import xbmc
import xbmcgui
from utils import logger

have_youtube_dl = "false"
try:
    import youtube_dl

    have_youtube_dl = "true"
except ImportError:
    logger.info("Youtube dl not present")


def run(argument):
    if argument['type'] == 'magnet':
        handle_magnet(argument['data'])
    elif argument['type'] == 'unresolvedurl':
        if ('queue' not in argument) or (argument['queue'] == "false"):
            action = "play"
        else:
            action = "queue"
        handle_unresolved_url(argument['data'], action)


def handle_magnet(data):
    open_with = utils.get_setting('openMagnetWith')
    logger.info('Sharing magnet with %s' % open_with)
    if open_with == 'Elementum':
        utils.call_plugin('plugin://plugin.video.elementum/playuri?uri=' + data)
    elif open_with == 'Torrenter V2':
        utils.call_plugin('plugin://plugin.video.torrenter/?action=playSTRM&url=' + data)
    elif open_with == 'Quasar':
        utils.call_plugin('plugin://plugin.video.quasar/playuri?uri=' + data)
    elif open_with == 'YATP':
        utils.call_plugin('plugin://plugin.video.yatp/?action=play&torrent=' + data + '&file_index=dialog')


def handle_unresolved_url(data, action):
    url = urllib.unquote(data)
    logger.info('Trying to resolve with urlresolver: %s' % url)
    stream_url = urlresolver.HostedMediaFile(url=url).resolve()
    if not stream_url:
        if have_youtube_dl == "false":
            logger.error("Url not resolved and no YoutubeDL: %s" % url)
        else:
            logger.info('Trying to resolve with YoutubeDL: %s' % url)
            youtube_dl_resolver = youtube_dl.YoutubeDL({'format': 'best', 'no_color': 'true'})
            youtube_dl_resolver.add_default_info_extractors()
            try:
                result = youtube_dl_resolver.extract_info(url, download=False)
            except Exception as e:
                logger.error("Error with YoutubeDL_resolver: %s" % e)
                result = []
            if "url" in result:
                stream_url = result["url"]
                logger.info("Url resolved by YoutubeDL: %s" % result)
            else:
                logger.error("Url not resolved by YoutubeDL: %s" % url)
    else:
        logger.info("Url resolved by urlResolver: %s" % stream_url)
    if not stream_url:
        logger.info("Trying to play as basic url: %s" % url)
        stream_url = url
    if stream_url:
        if (action == "play") or (not xbmc.Player().isPlaying()):
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
