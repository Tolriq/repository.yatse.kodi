# -*- coding: utf-8 -*-
import lib.private.ydlfix
import lib.utils as utils
import xbmc
import xbmcaddon
from lib.utils import logger
from lib.youtube_dl import YoutubeDL

lib.private.ydlfix.patch_youtube_dl()

if utils.is_python_3():
    from urllib.parse import unquote
else:
    from urllib import unquote

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
    if (utils.get_setting('useCookiesFromBrowser') == 'true'):
        browserName = utils.get_setting('cookiesBrowserName')

        if browserName:
            parameters['cookiesfrombrowser'] = [browserName]

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
    url = unquote(data)

    if utils.get_setting('preferArteAddon') == 'true' and "arte.tv" in url:
        ARTE_PLUGIN_ID = 'plugin.video.tyl0re.arte'
        if utils.addon_exists(ARTE_PLUGIN_ID):
            logger.info(u'Passing URL (%s) to ARTE Plugin (%s) as per current user settings' % (url,ARTE_PLUGIN_ID))
            xbmc.Player().play('plugin://%s/?mode=playVideo&url=%s' % (ARTE_PLUGIN_ID,url))
            return True
        else:
            errmsg='Arte addon is not installed. Passing URL to regular handling. Please install Arte addon manually or deactivate using Arte arte in settings'
            logger.error(errmsg)
            utils.show_error_notification(errmsg)
    
    logger.info(u'Trying to resolve URL (%s): %s' % (action, url))
    if xbmc.Player().isPlaying():
        utils.show_info_notification(utils.translation(32007), 1000)
    else:
        utils.show_info_notification(utils.translation(32007))
    if 'youtube.com' in url or 'youtu.be' in url:
        youtube_addon = xbmcaddon.Addon(id="plugin.video.youtube")
        if youtube_addon:
            if utils.get_setting('preferYoutubeAddon') == 'true' or youtube_addon.getSetting("kodion.video.quality.mpd") == "true":
                logger.info(u'Youtube addon have DASH enabled or is configured as preferred use it')
                utils.play_url('plugin://plugin.video.youtube/uri2addon/?uri=%s' % data, action)
                return

    media_filter = utils.get_setting('YoutubeDLCustomMediaFilter')
    if utils.get_setting('useYoutubeDLCustomFilter') == 'true' and media_filter:
        logger.info(u'Trying to resolve with YoutubeDL (Preferred YoutubeDL media format filter: %s)' % (media_filter) )
        result = resolve_with_youtube_dl(url, {'format': media_filter, 'no_color': 'true', 'ignoreerrors': 'true'}, action)
    else:
        logger.info(u'Trying to resolve with YoutubeDL (Default Setting)')
        result = resolve_with_youtube_dl(url, {'format': 'best', 'no_color': 'true', 'ignoreerrors': 'true'}, action)
    if result:
        return

    # Second pass with new params to fix site like reddit dash streams
    logger.info(u'Trying to resolve with YoutubeDL other options')
    result = resolve_with_youtube_dl(url, {'format': 'bestvideo+bestaudio/best', 'no_color': 'true', 'ignoreerrors': 'true'}, action)
    if result:
        return
    logger.error(u'Url not resolved by YoutubeDL')

    logger.info(u'Trying to play as basic url')
    utils.play_url(url, action)
    if url:
        utils.show_error_notification(utils.translation(32006))
