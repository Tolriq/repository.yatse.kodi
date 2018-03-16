# -*- coding: utf-8 -*-
import urllib

import urlresolver
import utils
from utils import logger

have_youtube_dl = "false"
try:
    # noinspection PyUnresolvedReferences
    import youtube_dl

    have_youtube_dl = "true"
except ImportError:
    logger.info("YoutubeDL not present")


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
    if have_youtube_dl == "true":
        logger.info('Trying to resolve with YoutubeDL: %s' % url)
        youtube_dl_resolver = youtube_dl.YoutubeDL({'format': 'best', 'no_color': 'true'})
        youtube_dl_resolver.add_default_info_extractors()
        try:
            result = youtube_dl_resolver.extract_info(url, download=False)
        except Exception as e:
            logger.error("Error with YoutubeDL: %s" % e)
            result = {}
        if "url" in result:
            logger.info("Url resolved by YoutubeDL: %s" % result)
            utils.play_url(result['url'], action)
            return
        else:
            logger.error("Url not resolved by YoutubeDL: %s" % url)

    logger.info('Trying to resolve with urlResolver: %s' % url)
    stream_url = urlresolver.HostedMediaFile(url=url).resolve()
    if stream_url:
        logger.info("Url resolved by urlResolver: %s" % stream_url)
        utils.play_url(stream_url, action)
        return

    logger.info("Trying to play as basic url: %s" % url)
    utils.play_url(url, action)
