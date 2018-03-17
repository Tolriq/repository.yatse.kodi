# -*- coding: utf-8 -*-
import sys

sys.argv.insert(1, 0)  # Stupid hack as calling scripts from JSON does not add script handle

import xbmcgui
from lib import share
from lib import utils
from lib.utils import logger, translation

logger.info("Starting script version: %s", utils.ADDON_VERSION)

argument = {}
for arg in sys.argv[2:]:
    argInfo = arg.split('=')
    argument[argInfo[0]] = argInfo[1]

logger.info("Parameters: %s" % argument)

commands = {'share': share.run}

if argument['action'] in commands:
    commands[argument['action']](argument)
else:
    logger.error("Command not supported: %s" % argument['action'])
    xbmcgui.Dialog().ok(utils.ADDON_NAME, translation(32004), translation(32005))
