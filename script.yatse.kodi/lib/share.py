# -*- coding: utf-8 -*-
import urllib

import urlresolver
import utils
import xbmcgui
from utils import logger, KODI_VERSION

have_youtube_dl = False
try:
    # noinspection PyUnresolvedReferences
    import youtube_dl

    try:
        import private.ydlfix

        private.ydlfix.patch_youtube_dl()
        logger.info('YoutubeDL patched!')
    except Exception as ex:
        logger.error('YoutubeDL not patched: %s' % ex)

    have_youtube_dl = True
except ImportError:
    logger.info('YoutubeDL not present')


def run(argument):
    if argument['type'] == 'magnet':
        handle_magnet(argument['data'])
    elif argument['type'] == 'unresolvedurl':
        if ('queue' not in argument) or (argument['queue'] == 'false'):
            action = 'play'
        else:
            action = 'queue'
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
    if not utils.kodi_is_playing():
        if KODI_VERSION <= 16:
            dialog = xbmcgui.DialogProgress()
            dialog.create("YATSE", "%s %s" % (action, url))
        else:
            dialog = xbmcgui.DialogBusy()
            dialog.create()
        dialog.update(-1)
    else:
        dialog = None
    if have_youtube_dl:
        logger.info(u'Trying to resolve with YoutubeDL: %s' % url)
        youtube_dl_resolver = youtube_dl.YoutubeDL({'format': 'bestvideo/bestaudio/best', 'no_color': 'true', 'ignoreerrors': 'true'})
        youtube_dl_resolver.add_default_info_extractors()
        try:
            result = youtube_dl_resolver.extract_info(url, download=False)
        except Exception as e:
            logger.error(u'Error with YoutubeDL: %s' % e)
            result = {}
        if result is not None and 'entries' in result:
            logger.info(u'Playlist resolved by YoutubeDL: %s items' % len(result['entries']))
            item_list = []
            if result is not None:
                for entry in result['entries']:
                    if entry is not None and 'url' in entry:
                        item_list.append(entry)
                        logger.info(u'Media found: %s' % entry['url'])
            if len(item_list) > 0:
                utils.play_items(item_list, action)
                if dialog is not None:
                    dialog.close()
                return
            else:
                logger.info(u'No playable urls in the playlist')
        if result is not None and 'url' in result:
            logger.info(u'Url resolved by YoutubeDL: %s' % result['url'])
            utils.play_url(result['url'], action, result)
            if dialog is not None:
                dialog.close()
            return
        logger.error(u'Url not resolved by YoutubeDL: %s' % url)

    logger.info(u'Trying to resolve with urlResolver: %s' % url)
    stream_url = urlresolver.HostedMediaFile(url=url).resolve()
    if stream_url:
        logger.info(u'Url resolved by urlResolver: %s' % stream_url)
        utils.play_url(stream_url, action)
        if dialog is not None:
            dialog.close()
        return

    logger.info(u'Trying to play as basic url: %s' % url)
    utils.play_url(url, action)
    if dialog is not None:
        dialog.close()
