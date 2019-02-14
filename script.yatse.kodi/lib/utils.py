# -*- coding: utf-8 -*-
import logging
import re

import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_ID = ADDON.getAddonInfo('id')
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion").split()[0][:2])


class XBMCHandler(logging.StreamHandler):
    xbmc_levels = {
        'DEBUG': 0,
        'INFO': 2,
        'WARNING': 3,
        'ERROR': 4,
        'LOGCRITICAL': 5,
    }

    def emit(self, record):
        xbmc_level = self.xbmc_levels.get(record.levelname)
        if isinstance(record.msg, unicode):
            record.msg = record.msg.encode('utf-8')
        if get_setting('logEnabled') == 'true':
            xbmc.log(self.format(record), xbmc_level)


handler = XBMCHandler()
handler.setFormatter(logging.Formatter('[' + ADDON_ID + '] %(message)s'))
logger = logging.getLogger(ADDON_ID)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_setting(key):
    return ADDON.getSetting(key)


def call_plugin(plugin):
    logger.info(u'Calling plugin: %s' % plugin)
    xbmc.executebuiltin('XBMC.RunPlugin(%s)' % plugin)


def translation(id_value):
    """ Utility method to get translations

    Args:
        id_value (int): Code of translation to get

    Returns:
        str: Translated string
    """
    return ADDON.getLocalizedString(id_value)


def show_info_notification(message, duration=3000):
    xbmcgui.Dialog().notification(ADDON_NAME, message, xbmcgui.NOTIFICATION_INFO, duration, False)


def show_error_notification(message):
    xbmcgui.Dialog().notification(ADDON_NAME, message, xbmcgui.NOTIFICATION_ERROR, 4000, False)


def kodi_is_playing():
    return xbmc.Player().isPlaying()


def play_url(url, action, meta_data=None, use_adaptive=False):
    if meta_data is not None:
        list_item = get_kodi_list_item(meta_data)
        if use_adaptive:
            list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    else:
        list_item = None
        if use_adaptive:
            list_item = xbmcgui.ListItem(path=url)
            list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
    if url:
        if (action == 'play') or (not xbmc.Player().isPlaying()):
            logger.info(u'Playing url: %s' % url)
            # Clear both playlist but only fill video as mixed playlist will work and audio will correctly play
            xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            if list_item is not None:
                if list_item.getProperty('yatse_picture'):
                    play_picture(list_item)
                    return
                playlist.add(url, list_item)
            else:
                playlist.add(url)
            xbmc.Player().play(playlist)
        else:
            if xbmc.Player().isPlayingAudio():
                logger.info(u'Queuing url to music: %s' % url)
                playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
                if list_item is not None:
                    playlist.add(url, list_item)
                else:
                    playlist.add(url)
            else:
                logger.info(u'Queuing url to video: %s' % url)
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                if list_item is not None:
                    playlist.add(url, list_item)
                else:
                    playlist.add(url)
    else:
        show_error_notification(translation(32006))


def play_items(items, action):
    if (action == 'play') or (not xbmc.Player().isPlaying()):
        logger.info(u'Playing %s items' % len(items))
        # Clear both playlist but only fill video as mixed playlist will work and audio will correctly play
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        for item in items:
            list_item = get_kodi_list_item(item)
            if list_item.getProperty('yatse_picture'):
                play_picture(list_item)
                return
            playlist.add(get_list_item_path(list_item), list_item)
        xbmc.Player().play(playlist)
    else:
        if xbmc.Player().isPlayingAudio():
            logger.info(u'Queuing %s items to music' % len(items))
            playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
            for item in items:
                list_item = get_kodi_list_item(item)
                playlist.add(get_list_item_path(list_item), list_item)
        else:
            logger.info(u'Queuing %s items to video' % len(items))
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            for item in items:
                list_item = get_kodi_list_item(item)
                playlist.add(get_list_item_path(list_item), list_item)


def get_kodi_list_item(meta_data):
    list_item = xbmcgui.ListItem()
    item_info = {}
    is_audio = False
    is_picture = False
    if 'title' in meta_data:
        list_item.setLabel(meta_data['title'])
        item_info['title'] = meta_data['title']
    if 'thumbnail' in meta_data:
        list_item.setThumbnailImage(meta_data['thumbnail'])
    if 'duration' in meta_data:
        item_info['duration'] = meta_data['duration']
    if 'url' in meta_data:
        list_item.setPath(meta_data['url'])
    if 'categories' in meta_data:
        item_info['genre'] = meta_data['categories']
    if 'average_rating' in meta_data:
        item_info['rating'] = meta_data['average_rating']

    mime_type = None
    if 'mime_type' in meta_data:
        mime_type = meta_data['mime_type']
    elif 'ext' in meta_data:
        mime_type = get_mime_type(meta_data['ext'])

    if 'media_type' in meta_data:
        is_audio = meta_data['media_type'] == 'audio'
        is_picture = meta_data['media_type'] == 'picture'
    elif mime_type is not None:
        is_audio = mime_type.startswith('audio')
        is_picture = mime_type.startswith('image')

    if is_audio:
        if 'artist' in meta_data:
            item_info['artist'] = meta_data['artist']
        if 'album' in meta_data:
            item_info['album'] = meta_data['album']
        if 'track_number' in meta_data:
            item_info['tracknumber'] = meta_data['track_number']
    elif not is_picture:
        if 'description' in meta_data:
            try:
                item_info['plot'] = re.sub('<[^<]+?>', '', meta_data['description'])
            except Exception as ex:
                logger.error('Problem with description: %s', ex)
                pass

    if KODI_VERSION >= 16 and mime_type is not None and (mime_type.startswith('audio') or mime_type.startswith('video') or mime_type.startswith('image')):
        list_item.setMimeType(mime_type)
        list_item.setContentLookup(False)

    if len(item_info) > 0:
        logger.info('Is audio: %s | Is picture: %s' % (is_audio, is_picture))
        if is_audio:
            list_item.setInfo('music', item_info)
        elif is_picture:
            list_item.setProperty('yatse_picture', 'true')
            list_item.setInfo('pictures', item_info)
        else:
            list_item.setInfo('video', item_info)

    return list_item


def play_picture(list_item):
    if xbmcgui.getCurrentWindowDialogId() == 12007 and KODI_VERSION >= 18:
        xbmc.executeJSONRPC('[{"id":1,"jsonrpc":"2.0","method":"Playlist.add","params":{"playlistid":2,"item":{"file":"%s"}}},{"id":2,"jsonrpc":"2.0","method":"Player.GoTo","params":{"to":"next","playerid":2}}]' % get_list_item_path(list_item))
    else:
        xbmc.executeJSONRPC('{"id":1,"jsonrpc":"2.0","method":"Player.Open","params":{"item":{"file":"%s"}}}' % get_list_item_path(list_item))


def get_mime_type(extension):
    try:
        import mimetypes
        mimetypes.init()
        return mimetypes.guess_type('File.' + str(extension), False)[0]
    except Exception as ex:
        logger.error('Error: %s', ex)
        return None


def get_list_item_path(list_item):
    if KODI_VERSION >= 17:
        return list_item.getPath()
    else:
        return list_item.getfilename()
