# -*- coding: utf-8 -*-
import sys
import xbmcgui

from lib import utils
from lib import share
from lib.utils import logger

logger.info("Starting script version: %s", utils.ADDON_VERSION)

argument = {}
for arg in sys.argv[1:]:
    argInfo = arg.split('=')
    argument[argInfo[0]] = argInfo[1]

logger.info("Parameters: %s" % argument)

commands = { 'share' : share.run }

if argument['action'] in commands:
	commands[argument['action']](argument)
else:
	logger.error("Command not supported: %s" % argument['action'])
	xbmcgui.Dialog().ok(utils.ADDON_NAME, "Unsupported command received.", "Please verify if there's an update for this plugin.")