# -*- coding: utf-8 -*-
import urllib

import private.ydlfix
import urlresolver
import utils
import xbmc
import xbmcaddon
from utils import logger
from youtube_dl import YoutubeDL

private.ydlfix.patch_youtube_dl()

have_adaptive_plugin = '"enabled":true' in xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","id":1,"params":{"addonid":"inputstream.adaptive", "properties": ["enabled"]}}')


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


def resolve_with_youtube_dl(url, parameters, action):
    youtube_dl_resolver = YoutubeDL(parameters)
    youtube_dl_resolver.add_default_info_extractors()
    try:
        result = youtube_dl_resolver.extract_info(url, download=False)
        if result is None:
            result = {}
    except Exception as e:
        logger.error(u'Error with YoutubeDL: %s' % e)
        result = {}
    logger.info(u'YoutubeDL full result: %s' % result)
    if 'entries' in result:
        logger.info(u'Playlist resolved by YoutubeDL: %s items' % len(result['entries']))
        item_list = []
        for entry in result['entries']:
            if entry is not None and 'url' in entry:
                item_list.append(entry)
                logger.info(u'Media found: %s' % entry['url'])
        if len(item_list) > 0:
            utils.play_items(item_list, action)
            return True
        else:
            logger.info(u'No playable urls in the playlist')
    if 'url' in result:
        logger.info(u'Url resolved by YoutubeDL: %s' % result['url'])
        utils.play_url(result['url'], action, result)
        return True
    if 'requested_formats' in result:
        if have_adaptive_plugin:
            logger.info(u'Adaptive plugin enabled looking for dash content')
            for entry in result['requested_formats']:
                if 'container' in entry and 'manifest_url' in entry:
                    if 'dash' in entry['container']:
                        logger.info(u'Url resolved by YoutubeDL: %s' % entry['manifest_url'])
                        utils.play_url(entry['manifest_url'], action, result, True)
                        return True
        for entry in result['requested_formats']:
            if 'protocol' in entry and 'manifest_url' in entry:
                if 'm3u8' in entry['protocol']:
                    logger.info(u'Url resolved by YoutubeDL: %s' % entry['manifest_url'])
                    utils.play_url(entry['manifest_url'], action, result)
                    return True
    return False


def handle_unresolved_url(data, action):
    url = urllib.unquote(data)
    logger.info(u'Trying to resolve URL (%s): %s' % (action, url))
    if xbmc.Player().isPlaying():
        utils.show_info_notification(utils.translation(32007), 1000)
    else:
        utils.show_info_notification(utils.translation(32007))
    if 'youtube.com' in url or 'youtu.be' in url:
        youtube_addon = xbmcaddon.Addon(id="plugin.video.youtube")
        if youtube_addon:
            if youtube_addon.getSetting("kodion.video.quality.mpd") == "true":
                logger.info(u'Youtube addon have DASH enabled use it')
                utils.play_url('plugin://plugin.video.youtube/uri2addon/?uri=%s' % url, action)
                return
    logger.info(u'Trying to resolve with YoutubeDL')
    result = resolve_with_youtube_dl(url, {'format': 'best', 'no_color': 'true', 'ignoreerrors': 'true'}, action)
    if result:
        return
    # Second pass with new params to fix site like reddit dash streams
    logger.info(u'Trying to resolve with YoutubeDL other options')
    result = resolve_with_youtube_dl(url, {'format': 'bestvideo+bestaudio/best', 'no_color': 'true', 'ignoreerrors': 'true'}, action)
    if result:
        return
    logger.error(u'Url not resolved by YoutubeDL')

    logger.info(u'Trying to resolve with urlResolver')
    stream_url = urlresolver.HostedMediaFile(url=url).resolve()
    if stream_url:
        logger.info(u'Url resolved by urlResolver: %s' % stream_url)
        utils.play_url(stream_url, action)
        return

    logger.info(u'Trying to play as basic url')
    utils.play_url(url, action)
    if url:
        utils.show_error_notification(utils.translation(32006))
