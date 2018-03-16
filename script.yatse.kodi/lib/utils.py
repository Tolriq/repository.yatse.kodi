# -*- coding: utf-8 -*-
import logging

import xbmc
import xbmcaddon
import xbmcgui

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_ID = ADDON.getAddonInfo('id')


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


def kodi_is_playing():
    return xbmc.Player().isPlaying()


def play_url(url, action, meta_data=None):
    if meta_data is not None:
        list_item = get_kodi_list_item(meta_data)
    else:
        list_item = None
    if url:
        if (action == 'play') or (not xbmc.Player().isPlaying()):
            logger.info(u'Playing url: %s' % url)
            # Clear both playlist but only fill video as mixed playlist will work and audio will correctly play
            xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            playlist.clear()
            if list_item is not None:
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
        dialog = xbmcgui.Dialog()
        dialog.notification(ADDON_NAME, translation(32006), xbmcgui.NOTIFICATION_INFO, 5000)


def play_items(items, action):
    if (action == 'play') or (not xbmc.Player().isPlaying()):
        logger.info(u'Playing %s items' % len(items))
        # Clear both playlist but only fill video as mixed playlist will work and audio will correctly play
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        for item in items:
            list_item = get_kodi_list_item(item)
            playlist.add(list_item.getPath(), list_item)
        xbmc.Player().play(playlist)
    else:
        if xbmc.Player().isPlayingAudio():
            logger.info(u'Queuing %s items to music' % len(items))
            playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
            for item in items:
                list_item = get_kodi_list_item(item)
                playlist.add(list_item.getPath(), list_item)
        else:
            logger.info(u'Queuing %s items to video' % len(items))
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            for item in items:
                list_item = get_kodi_list_item(item)
                playlist.add(list_item.getPath(), list_item)


def get_kodi_list_item(meta_data):
    list_item = xbmcgui.ListItem()
    item_info = {}
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

    if len(item_info) > 0:
        list_item.setInfo('music', item_info)
        list_item.setInfo('video', item_info)

    return list_item
