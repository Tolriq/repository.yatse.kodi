# -*- coding: utf-8 -*-
import logging

import xbmc
import xbmcaddon

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
        if get_setting("logEnabled") == "true":
            xbmc.log(self.format(record), xbmc_level)


handler = XBMCHandler()
handler.setFormatter(logging.Formatter('[' + ADDON_ID + '] %(message)s'))
logger = logging.getLogger(ADDON_ID)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def get_setting(key):
    return ADDON.getSetting(key)


def call_plugin(plugin):
    logger.info('Calling plugin: %s' % plugin)
    xbmc.executebuiltin('XBMC.RunPlugin(%s)' % plugin)


def translation(id_value):
    """ Utility method to get translations

    Args:
        id_value (int): Code of translation to get

    Returns:
        str: Translated string
    """
    return ADDON.getLocalizedString(id_value)
